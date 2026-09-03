#
# Copyright (C) 2010-2016 CEA/DAM
# Copyright (C) 2010-2016 Aurelien Degremont <aurelien.degremont@cea.fr>
# Copyright (C) 2015-2017 Stephane Thiell <sthiell@stanford.edu>
#
# This file is part of ClusterShell.
#
# ClusterShell is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# ClusterShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with ClusterShell; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
Cluster nodes utility module

The NodeUtils module is a ClusterShell helper module that provides
supplementary services to manage nodes in a cluster. It is primarily
designed to enhance the NodeSet module providing some binding support
to external node groups sources in separate namespaces (example of
group sources are: files, jobs scheduler, custom scripts, etc.).
"""

try:
    from configparser import ConfigParser, NoOptionError, NoSectionError
except ImportError:
    # Python 2 compat
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError

import errno
from functools import wraps
import glob
import logging
import os
import time
import warnings

from string import Template
from subprocess import Popen, PIPE

# compat with python 2.7, import directly above for 3.x
try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'r')

# compat with python 2.7, use str directly in 3.x
try:
    basestring
except NameError:
    basestring = str

from ClusterShell.Defaults import _expand_dirs


LOGGER = logging.getLogger(__name__)

# cap on recorded ignored group names, per group source
_IGN_GRP_MAX = 100


class GroupSourceError(Exception):
    """Base GroupSource error exception"""
    def __init__(self, message, group_source):
        Exception.__init__(self, message)
        self.group_source = group_source

class GroupSourceNoUpcall(GroupSourceError):
    """Raised when upcall or method is not available"""

class GroupSourceQueryFailed(GroupSourceError):
    """Raised when a query failed (eg. no group found)"""

class GroupResolverError(Exception):
    """Base GroupResolver error"""

class GroupResolverSourceError(GroupResolverError):
    """Raised when upcall is not available"""

class GroupResolverIllegalCharError(GroupResolverError):
    """Raised when an illegal group character is encountered (no longer
    raised by ClusterShell as of version 1.11, kept for compatibility)"""

class GroupResolverConfigError(GroupResolverError):
    """Raised when a configuration error is encountered"""


_DEFAULT_CACHE_TIME = 3600


class GroupSource(object):
    """ClusterShell Group Source class.

    A Group Source object defines resolv_map, resolv_list, resolv_all and
    optional resolv_reverse methods for node group resolution. It is
    constituting a group resolution namespace.
    """

    def __init__(self, name, groups=None, allgroups=None):
        """Initialize GroupSource

        :param name: group source name
        :param groups: group to nodes dict
        :param allgroups: optional "all groups" result (string)
        """
        self.name = name
        self.groups = groups or {} # we avoid the use of {} as default argument
        self.allgroups = allgroups
        self.has_reverse = False
        self._illegal_ignored = {}  # ignored group names {name: chars}

    def resolv_map(self, group):
        """Get nodes from group `group`"""
        return self.groups.get(group, '')

    def resolv_list(self):
        """Return a list of all group names for this group source"""
        return list(self.groups)

    def resolv_all(self):
        """Return the content of all groups as defined by this GroupSource"""
        if self.allgroups is None:
            raise GroupSourceNoUpcall("All groups info not available", self)
        return self.allgroups

    def resolv_reverse(self, node):
        """
        Return the group name matching the provided node.
        """
        raise GroupSourceNoUpcall("Not implemented", self)


class FileGroupSource(GroupSource):
    """File-based Group Source using loader for file format and cache expiry."""

    def __init__(self, name, loader):
        """
        Initialize FileGroupSource object.

        :param name: group source name (eg. key name of yaml root dict)
        :param loader: associated content loader (eg. YAMLGroupLoader object)
        """
        # do not call super.__init__ to allow the use of r/o properties
        self.name = name
        self.loader = loader
        self.has_reverse = False
        self._illegal_ignored = {}

    @property
    def groups(self):
        """groups property (dict)"""
        return self.loader.groups(self.name)

    @property
    def allgroups(self):
        """allgroups property (string)"""
        # FileGroupSource uses the 'all' group to implement resolv_all
        return self.groups.get('all')


class UpcallGroupSource(GroupSource):
    """
    GroupSource class managing external calls for nodegroup support.

    Upcall results are cached for a customizable amount of time. This is
    controlled by `cache_time` attribute. Default is 3600 seconds.

    The optional 'mapall' upcall returns all group-to-nodes mappings in a
    single call and is then used to serve both 'map' and 'list' queries
    from the cache.
    """

    def __init__(self, name, map_upcall=None, all_upcall=None,
                 list_upcall=None, reverse_upcall=None, cfgdir=None,
                 cache_time=None, mapall_upcall=None):
        GroupSource.__init__(self, name)
        self.verbosity = 0 # deprecated
        self.cfgdir = cfgdir
        self.logger = logging.getLogger(__name__)

        # Supported external upcalls
        self.upcalls = {}
        if map_upcall:
            self.upcalls['map'] = map_upcall
        if all_upcall:
            self.upcalls['all'] = all_upcall
        if list_upcall:
            self.upcalls['list'] = list_upcall
        if reverse_upcall:
            self.upcalls['reverse'] = reverse_upcall
            self.has_reverse = True
        if mapall_upcall:
            self.upcalls['mapall'] = mapall_upcall

        # Cache upcall data
        if cache_time is None:
            self.cache_time = _DEFAULT_CACHE_TIME
        else:
            self.cache_time = cache_time
        self._cache = {}
        self.clear_cache()

    def clear_cache(self):
        """
        Remove all previously cached upcall results whatever their lifetime
        is, along with any recorded ignored group names.
        """
        self._cache = {
            'map': {},
            'reverse': {}
        }
        self._illegal_ignored = {}

    def _upcall_read(self, cmdtpl, args=dict()):
        """
        Invoke the specified upcall command, raise an Exception if
        something goes wrong and return the command output otherwise.
        """
        cmdline = Template(self.upcalls[cmdtpl]).safe_substitute(args)
        self.logger.debug("EXEC '%s'", cmdline)
        proc = Popen(cmdline, stdin=DEVNULL, stdout=PIPE, shell=True,
                     cwd=self.cfgdir, universal_newlines=True)
        output = proc.communicate()[0].strip()
        self.logger.debug("READ '%s'", output)
        if proc.returncode != 0:
            self.logger.debug("ERROR '%s' returned %d", cmdline,
                              proc.returncode)
            raise GroupSourceQueryFailed(cmdline, self)
        return output

    def _upcall_cache(self, upcall, cache, key, **args):
        """
        Look for `key' in provided `cache'. If not found, call the
        corresponding `upcall'.

        If `key' is missing, it is added to provided `cache'. Each entry in a
        cache is kept only for a limited time equal to self.cache_time .
        """
        # Purge expired data from cache
        if key in cache and cache[key][1] < time.time():
            self.logger.debug("PURGE EXPIRED (%d)'%s'", cache[key][1], key)
            del cache[key]

        # Fetch the data if unknown of just purged
        if key not in cache:
            if not self.upcalls.get(upcall):
                raise GroupSourceNoUpcall(upcall, self)

            cache_expiry = time.time() + self.cache_time
            # $CFGDIR and $SOURCE always replaced
            args['CFGDIR'] = self.cfgdir
            args['SOURCE'] = self.name
            cache[key] = (self._upcall_read(upcall, args), cache_expiry)

        return cache[key][0]

    def _populate_from_mapall(self):
        """
        Run the optional 'mapall' upcall and fill the map and list caches
        from its output. No-op if 'mapall' is not defined or its last
        result is still fresh.
        """
        if 'mapall' not in self.upcalls:
            return
        cached = self._cache.get('mapall')
        if cached is not None and cached[1] >= time.time():
            return

        content = self._upcall_cache('mapall', self._cache, 'mapall')
        cache_expiry = self._cache['mapall'][1]
        new_map = {}
        try:
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                group, sep, nodes = line.partition(':')
                group = group.strip()
                if not sep or not group or len(group.split()) > 1:
                    raise GroupSourceQueryFailed(
                        "mapall: invalid line %r (expected 'group: nodes')"
                        % line, self)
                nodes = nodes.strip()
                if group in new_map:
                    # union duplicate group lines, like multi-line map output
                    nodes = ','.join(n for n in (new_map[group][0], nodes) if n)
                new_map[group] = (nodes, cache_expiry)
        except GroupSourceQueryFailed:
            del self._cache['mapall'] # do not keep unusable output
            raise
        self._cache['map'] = new_map
        self._cache['list'] = (' '.join(new_map), cache_expiry)

    def resolv_map(self, group):
        """
        Get nodes from group 'group', using the cached value if
        available.
        """
        self._populate_from_mapall()
        if 'map' not in self.upcalls and 'mapall' in self.upcalls:
            # no map fallback: unknown group resolves to an empty node set
            return self._cache['map'].get(group, ('',))[0]
        return self._upcall_cache('map', self._cache['map'], group, GROUP=group)

    def resolv_list(self):
        """
        Return a list of all group names for this group source, using
        the cached value if available.
        """
        self._populate_from_mapall()
        if 'list' not in self.upcalls and 'mapall' in self.upcalls:
            # no list fallback: read mapall result directly (cache_time 0)
            return self._cache['list'][0]
        return self._upcall_cache('list', self._cache, 'list')

    def resolv_all(self):
        """
        Return the content of special group ALL, using the cached value
        if available.
        """
        return self._upcall_cache('all', self._cache, 'all')

    def resolv_reverse(self, node):
        """
        Return the group name matching the provided node, using the
        cached value if available.
        """
        # Cast node to string as cache key must be hashable
        node_str = str(node)
        return self._upcall_cache('reverse', self._cache['reverse'], node_str,
                                  NODE=node_str)


class YAMLGroupLoader(object):
    """
    YAML group file loader/reloader.

    Load or reload a YAML multi group sources file:

    - create GroupSource objects
    - gather groups dict content on load
    - reload the file once cache_time has expired
    """

    def __init__(self, filename, cache_time=None):
        """
        Initialize YAMLGroupLoader and load file.

        :param filename: YAML file path
        :param cache_time: cache time (seconds)
        """
        if cache_time is None:
            self.cache_time = _DEFAULT_CACHE_TIME
        else:
            self.cache_time = cache_time
        self.cache_expiry = 0
        self.filename = filename
        self.sources = {}
        self._groups = {}
        # must be loaded after initialization so self.sources is set
        self._load()

    def _load(self):
        """Load or reload YAML group file to create GroupSource objects."""
        with open(self.filename) as yamlfile:
            try:
                import yaml
                sources = yaml.safe_load(yamlfile)
            except ImportError as exc:
                msg = "Disable autodir or install PyYAML!"
                raise GroupResolverConfigError("%s (%s)" % (str(exc), msg))
            except yaml.YAMLError as exc:
                raise GroupResolverConfigError("%s: %s" % (self.filename, exc))

        # NOTE: change to isinstance(sources, collections.Mapping) with py2.6+
        if not isinstance(sources, dict):
            fmt = "%s: invalid content (base is not a dict)"
            raise GroupResolverConfigError(fmt % self.filename)

        first = not self.sources

        for srcname, groups in sources.items():

            # check for valid types returned by PyYAML Loader
            if not isinstance(srcname, basestring):
                fmt = '%s: group source %s not a string (add quotes?)'
                raise GroupResolverConfigError(fmt % (self.filename, srcname))

            if not isinstance(groups, dict):
                fmt = "%s: invalid content (group source '%s' is not a dict)"
                raise GroupResolverConfigError(fmt % (self.filename, srcname))

            for grp, grpnodes in groups.items():
                if not isinstance(grp, basestring):
                    fmt = '%s: %s: group name %s not a string (add quotes?)'
                    raise GroupResolverConfigError(fmt % (self.filename,
                                                          srcname, grp))
                # GH#533: interpret null value as empty set
                if grpnodes is None:
                    groups[grp] = ''

            if first:
                self._groups[srcname] = groups
                self.sources[srcname] = FileGroupSource(srcname, self)
            elif srcname in self.sources:
                # update groups of existing source
                self._groups[srcname] = groups
            # else: cannot add new source on reload - just ignore it

        # groups are loaded, set cache expiry
        self.cache_expiry = time.time() + self.cache_time

    def __iter__(self):
        """Iterate over GroupSource objects."""
        # safe as long as self.sources is set at init (once)
        return iter(self.sources.values())

    def groups(self, sourcename):
        """
        Groups dict accessor for sourcename.

        This method is called by associated FileGroupSource objects and simply
        returns dict content, after reloading file if cache_time has expired.
        """
        if self.cache_expiry < time.time():
            # reload whole file if cache time expired
            self._load()

        return self._groups[sourcename]


class GroupResolver(object):
    """
    Base class GroupResolver that aims to provide node/group resolution
    from multiple GroupSources.

    A GroupResolver object might be initialized with a default
    GroupSource object, that is later used when group resolution is
    requested with no source information. As of version 1.7, a set of
    illegal group characters may also be provided for sanity check. As of
    version 1.11, group names containing illegal characters are ignored,
    recorded (see ignored_groups()) and logged as a warning (previous
    versions raised GroupResolverIllegalCharError).
    """

    def __init__(self, default_source=None, illegal_chars=None):
        """Lazy initialization of a new GroupResolver object."""
        self._sources = {}
        self._default_source = default_source
        self._initialized = False
        self.illegal_chars = illegal_chars or set()

    def _late_init(self):
        """Override method to initialize object just before it is needed."""
        if self._default_source:
            self._sources[self._default_source.name] = self._default_source
        self._initialized = True  # overriding methods should call super

    def init(func):
        @wraps(func)
        def wrapper(self, *args):
            if not self._initialized:
                self._late_init()
            return func(self, *args)
        return wrapper

    @init
    def set_verbosity(self, value):
        """Set debugging verbosity value (DEPRECATED: use logging.DEBUG)."""
        warnings.warn("set_verbosity() is deprecated; use logging instead",
                      DeprecationWarning, stacklevel=2)
        for source in self._sources.values():
            source.verbosity = value

    @init
    def add_source(self, group_source):
        """Add a GroupSource to this resolver."""
        if group_source.name in self._sources:
            raise ValueError("GroupSource '%s': name collision" % \
                             group_source.name)
        self._sources[group_source.name] = group_source

    @init
    def sources(self):
        """Get the list of all resolver source names. """
        srcs = list(self._sources)
        if srcs and srcs[0] is not self._default_source:
            srcs.remove(self._default_source.name)
            srcs.insert(0, self._default_source.name)
        return srcs

    @init
    def _get_default_source_name(self):
        """Get default source name of resolver."""
        if self._default_source is None:
            return None
        return self._default_source.name

    @init
    def _set_default_source_name(self, sourcename):
        """Set default source of resolver (by name)."""
        try:
            self._default_source = self._sources[sourcename]
        except KeyError:
            raise GroupResolverSourceError(sourcename)

    default_source_name = property(_get_default_source_name,
                                   _set_default_source_name)

    def _list_nodes(self, source, what, *args):
        """Helper method that returns a list of results (nodes) when
        the source is defined."""
        result = []
        assert source
        raw = getattr(source, 'resolv_%s' % what)(*args)
        if isinstance(raw, list):
            raw = ','.join(raw)
        for line in raw.splitlines():
            [result.append(x) for x in line.strip().split()]
        return result

    def _list_groups(self, source, what, *args):
        """Helper method that returns a list of results (groups) when
        the source is defined."""
        result = []
        assert source
        raw = getattr(source, 'resolv_%s' % what)(*args)

        try:
            grpiter = raw.splitlines()
        except AttributeError:
            grpiter = raw

        for line in grpiter:
            for grpstr in line.strip().split():
                badchars = self.illegal_chars.intersection(grpstr)
                if badchars:
                    # record and warn only once per group name and source
                    ignored = source._illegal_ignored
                    if grpstr not in ignored and len(ignored) < _IGN_GRP_MAX:
                        ignored[grpstr] = ' '.join(sorted(badchars))
                        LOGGER.warning('ignoring group "%s" from source "%s": '
                                       'illegal character(s) "%s"', grpstr,
                                       source.name, ignored[grpstr])
                    continue
                result.append(grpstr)
        return result

    @init
    def _source(self, namespace):
        """Helper method that returns the source by namespace name."""
        if not namespace:
            source = self._default_source
        else:
            source = self._sources.get(namespace)
        if not source:
            raise GroupResolverSourceError(namespace or "<default>")
        return source

    def group_nodes(self, group, namespace=None):
        """
        Find nodes for specified group name and optional namespace.
        """
        source = self._source(namespace)
        return self._list_nodes(source, 'map', group)

    def all_nodes(self, namespace=None):
        """
        Find all nodes. You may specify an optional namespace.
        """
        source = self._source(namespace)
        return self._list_nodes(source, 'all')

    def grouplist(self, namespace=None):
        """
        Get full group list. You may specify an optional
        namespace.
        """
        source = self._source(namespace)
        return self._list_groups(source, 'list')

    def has_node_groups(self, namespace=None):
        """
        Return whether finding group list for a specified node is
        supported by the resolver (in optional namespace).
        """
        try:
            return self._source(namespace).has_reverse
        except GroupResolverSourceError:
            return False

    def node_groups(self, node, namespace=None):
        """
        Find group list for specified node and optional namespace.
        """
        source = self._source(namespace)
        return self._list_groups(source, 'reverse', node)

    def ignored_groups(self):
        """
        Get group names ignored due to illegal characters, as a dict
        {source name: {group name: illegal characters}}, at most 100
        recorded per source. UpcallGroupSource.clear_cache() clears the
        record.
        """
        return dict((name, dict(src._illegal_ignored))
                    for name, src in self._sources.items()
                    if src._illegal_ignored)


class GroupResolverConfig(GroupResolver):
    """
    GroupResolver class that is able to automatically setup its
    GroupSource's from a configuration file. This is the default
    resolver for NodeSet.
    """
    SECTION_MAIN = 'Main'

    def __init__(self, filenames, illegal_chars=None):
        """
        Lazy init GroupResolverConfig object from filenames.
        """
        GroupResolver.__init__(self, illegal_chars=illegal_chars)

        self.filenames = filenames
        self.config = None
        self._origins = {}

    def _late_init(self):
        """
        Initialize object when needed. All accessible config filenames are
        merged, the last one having the highest priority.
        """
        GroupResolver._late_init(self)

        # support single or multiple config filenames
        if isinstance(self.filenames, basestring):
            filenames = [self.filenames]
        else:
            filenames = list(self.filenames)

        self.config = ConfigParser()
        parsed = self.config.read(filenames)

        # check if at least one parsable config file has been found, otherwise
        # continue with an empty self._sources
        if parsed:
            # config dirs of the search path, even those without groups.conf
            cfgdirs = []
            for filename in filenames:
                cfgdir = os.path.dirname(filename)
                if cfgdir not in cfgdirs:
                    cfgdirs.append(cfgdir)

            # sections and dir options belong to the last file defining them
            section_dirs = {}
            option_dirs = {}
            for filename in parsed:
                filecfg = ConfigParser()
                filecfg.read(filename)
                for section in filecfg.sections():
                    section_dirs[section] = os.path.dirname(filename)
                for opt in ('groupsdir', 'confdir', 'autodir'):
                    if filecfg.has_option(self.SECTION_MAIN, opt):
                        option_dirs[opt] = os.path.dirname(filename)

            # sections missed by the re-parse fall back to lowest priority
            for section in self.config.sections():
                section_dirs.setdefault(section, cfgdirs[0])

            self._parse_config(cfgdirs, section_dirs, option_dirs)

    def _parse_config(self, cfgdirs, section_dirs, option_dirs):
        """
        Load group sources from parsed config. Config directories cfgdirs
        are scanned in ascending priority: for each of them, the groups.conf
        sections it defines (per section_dirs), then its confdir entries and
        finally its autodir entries (both owned per option_dirs).
        """
        main = self.SECTION_MAIN
        confdirstr = autodirstr = ''
        confdir_owner = autodir_owner = cfgdirs[0]
        if self.config.has_option(main, 'groupsdir'):
            confdirstr = self.config.get(main, 'groupsdir')
            confdir_owner = option_dirs.get('groupsdir', cfgdirs[0])
        elif self.config.has_option(main, 'confdir'):
            confdirstr = self.config.get(main, 'confdir')
            confdir_owner = option_dirs.get('confdir', cfgdirs[0])
        if self.config.has_option(main, 'autodir'):
            autodirstr = self.config.get(main, 'autodir')
            autodir_owner = option_dirs.get('autodir', cfgdirs[0])

        loaded_confdirs = set()
        loaded_autodirs = set()
        for cfgdir in cfgdirs:
            # add sources declared directly in groups.conf
            sections = [section for section in self.config.sections()
                        if section_dirs.get(section) == cfgdir]
            self._sources_from_cfg(self.config, cfgdir, sections)

            for confdir in _expand_dirs(confdirstr, cfgdir, confdir_owner,
                                        loaded_confdirs):
                if not os.path.isdir(confdir):
                    # only the defining config directory is strictly checked
                    if os.path.exists(confdir):
                        if cfgdir == confdir_owner:
                            raise GroupResolverConfigError(
                                "Defined confdir %s is not a directory"
                                % confdir)
                        LOGGER.debug("ignoring confdir %s: not a directory",
                                     confdir)
                    continue
                # add sources declared in groups.conf.d file parts
                for groupsfn in sorted(glob.glob('%s/*.conf' % confdir)):
                    grpcfg = ConfigParser()
                    grpcfg.read(groupsfn) # ignore files that cannot be read
                    self._sources_from_cfg(grpcfg, confdir, grpcfg.sections())

            for autodir in _expand_dirs(autodirstr, cfgdir, autodir_owner,
                                        loaded_autodirs):
                if not os.path.isdir(autodir):
                    if os.path.exists(autodir):
                        if cfgdir == autodir_owner:
                            raise GroupResolverConfigError(
                                "Defined autodir %s is not a directory"
                                % autodir)
                        LOGGER.debug("ignoring autodir %s: not a directory",
                                     autodir)
                    continue
                # add auto sources declared in groups.d YAML files
                for autosfn in sorted(glob.glob('%s/*.yaml' % autodir)):
                    try:
                        self._sources_from_yaml(autosfn)
                    except IOError as exc:  # same as OSError in Python 3
                        # in Python 3 only, we could just catch PermissionError
                        if exc.errno in (errno.EACCES, errno.EPERM):
                            # ignore YAML files that we don't have access to
                            LOGGER.debug(exc)
                            continue

        # parse Main.default
        try:
            def_sourcename = self.config.get(main, 'default')
            # warning: default_source_name is a property
            self.default_source_name = def_sourcename
        except (NoSectionError, NoOptionError):
            pass
        except GroupResolverSourceError:
            if def_sourcename: # allow empty Main.default
                fmt = 'Default group source not found: "%s"'
                raise GroupResolverConfigError(fmt % def_sourcename)
        # pick random default source if not provided by config
        if not self.default_source_name and self._sources:
            self.default_source_name = list(self._sources)[0]

    def _add_config_source(self, group_source, origin):
        """
        Add a config-defined GroupSource to this resolver, origin being the
        directory it has been defined in. A group source defined in a
        previously scanned directory is overridden, but a name collision
        within the same directory is an error.
        """
        srcname = group_source.name
        prev_origin = self._origins.get(srcname)
        if prev_origin == origin:
            raise GroupResolverConfigError("GroupSource '%s': name collision"
                                           " in %s" % (srcname, origin))
        if prev_origin is not None:
            LOGGER.debug("group source '%s' in %s overrides definition in %s",
                         srcname, origin, prev_origin)
        self._origins[srcname] = origin
        self._sources[srcname] = group_source

    def _sources_from_cfg(self, cfg, cfgdir, sections):
        """
        Instantiate as many UpcallGroupSources needed from the sections of
        cfg object, cfgdir being the directory they are defined in ($CFGDIR
        for upcalls).
        """
        try:
            for section in sections:
                # Support grouped sections: section1,section2,section3
                for srcname in section.split(','):
                    if srcname != self.SECTION_MAIN:
                        # map or mapall is a mandatory upcall
                        if not cfg.has_option(section, 'map') and \
                           not cfg.has_option(section, 'mapall'):
                            raise GroupResolverConfigError(
                                "No option 'map' or 'mapall' in section: %r"
                                % section)

                        map_upcall = mapall_upcall = None
                        all_upcall = list_upcall = reverse_upcall = ctime = None
                        if cfg.has_option(section, 'map'):
                            map_upcall = cfg.get(section, 'map', raw=True)
                        if cfg.has_option(section, 'mapall'):
                            mapall_upcall = cfg.get(section, 'mapall',
                                                    raw=True)
                        if cfg.has_option(section, 'all'):
                            all_upcall = cfg.get(section, 'all', raw=True)
                        if cfg.has_option(section, 'list'):
                            list_upcall = cfg.get(section, 'list', raw=True)
                        if cfg.has_option(section, 'reverse'):
                            reverse_upcall = cfg.get(section, 'reverse',
                                                     raw=True)
                        if cfg.has_option(section, 'cache_time'):
                            ctime = float(cfg.get(section, 'cache_time',
                                                  raw=True))
                        # add new group source
                        self._add_config_source(UpcallGroupSource(
                            srcname, map_upcall, all_upcall, list_upcall,
                            reverse_upcall, cfgdir, ctime,
                            mapall_upcall=mapall_upcall), cfgdir)
        except (NoSectionError, NoOptionError, ValueError) as exc:
            raise GroupResolverConfigError(str(exc))

    def _sources_from_yaml(self, filepath):
        """Load source(s) from YAML file."""
        autodir = os.path.dirname(filepath)
        for source in YAMLGroupLoader(filepath):
            self._add_config_source(source, autodir)
