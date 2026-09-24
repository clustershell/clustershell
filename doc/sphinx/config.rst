Configuration
=============

.. highlight:: ini

clush
-----

.. _clush-config:

clush.conf
^^^^^^^^^^

The *clush.conf* files are parsed with Python's `ConfigParser`_

Locations
"""""""""

The following configuration file defines system-wide default values for
several ``clush`` tool parameters::

    /etc/clustershell/clush.conf

``clush`` settings might then be overridden (globally, or per user) if one of
the following files is found, in priority order::

    $XDG_CONFIG_HOME/clustershell/clush.conf
    $HOME/.config/clustershell/clush.conf (only if $XDG_CONFIG_HOME is not defined)
    {sys.prefix}/etc/clustershell/clush.conf
    $HOME/.local/etc/clustershell/clush.conf

.. note:: The path using `sys.prefix`_ was added in version 1.9.1 and is
   useful for Python virtual environments. The per-user ``$HOME/.clush.conf``
   file of older versions is no longer read since version 1.9.

If the environment variable ``$CLUSTERSHELL_CFGDIR`` is defined, the following
configuration file is used instead of ``/etc/clustershell/clush.conf``; it
takes precedence over the files installed under `sys.prefix`_ and
``$HOME/.local``, and is only overridden by the per-user configuration file::

    $CLUSTERSHELL_CFGDIR/clush.conf

.. note:: ``$CLUSTERSHELL_CFGDIR`` replaces the system-wide configuration
   directory only: since version 1.11, ``/etc/clustershell`` is not read when
   it is defined, and the per-user configuration files override it just like
   they override ``/etc/clustershell``. To run ClusterShell with a fully
   controlled configuration, for example in tests, also point ``$HOME`` and
   ``$XDG_CONFIG_HOME`` to a scratch directory so that no user configuration
   file is found (the configuration directory under `sys.prefix`_ is still
   read).

Settings
""""""""

Settings that apply to all ``clush`` :ref:`run modes <clushmode-config>` are
contained within the ``[Main]`` section.

The following table describes available ``clush`` config file settings.

+-----------------+----------------------------------------------------+
| Key             | Value                                              |
+=================+====================================================+
| fanout          | Size of the sliding window of connectors (e.g. max |
|                 | number of *ssh(1)* allowed to run at the same      |
|                 | time).                                             |
+-----------------+----------------------------------------------------+
| confdir         | Optional list of directory paths where ``clush``   |
|                 | should look for **.conf** files which define       |
|                 | :ref:`run modes <clushmode-config>` that can then  |
|                 | be activated with `--mode`. All other ``clush``    |
|                 | config file settings defined in this table might   |
|                 | be overridden in a run mode. Each mode section     |
|                 | should have a name prefixed by "mode:" to clearly  |
|                 | identify a section defining a mode. Duplicate      |
|                 | modes are not allowed in those files.              |
|                 | Configuration files that are not readable by the   |
|                 | current user are ignored. Entries containing the   |
|                 | variable ``$CFGDIR`` are expanded once for each    |
|                 | configuration directory of the search path (since  |
|                 | version 1.11), so a user configuration directory is|
|                 | scanned even without a user *clush.conf* file.     |
|                 | Entries without ``$CFGDIR`` are scanned along with |
|                 | the configuration directory of the file defining   |
|                 | the option, and each directory is scanned only     |
|                 | once. The default *confdir* value enables both     |
|                 | system-wide and any installed user configuration   |
|                 | (thanks to ``$CFGDIR``).                           |
+-----------------+----------------------------------------------------+
| connect_timeout | Timeout in seconds to allow a connection to        |
|                 | establish. This parameter is passed to *ssh(1)*.   |
|                 | If set to 0, no timeout occurs.                    |
+-----------------+----------------------------------------------------+
| command_prefix  | Command prefix. Generally used for specific        |
|                 | :ref:`run modes <clush-modes>`, for example to     |
|                 | implement *sudo(8)* support.                       |
+-----------------+----------------------------------------------------+
| command_timeout | Timeout in seconds to allow a command to complete  |
|                 | since the connection has been established. This    |
|                 | parameter is passed to *ssh(1)*. In addition, the  |
|                 | ClusterShell library ensures that any commands     |
|                 | complete in less than (connect_timeout \+          |
|                 | command_timeout). If set to 0, no timeout occurs.  |
+-----------------+----------------------------------------------------+
| color           | Whether to use ANSI colors to surround node        |
|                 | or nodeset prefix/header with escape sequences to  |
|                 | display them in color on the terminal. Valid       |
|                 | arguments are *never*, *always* or *auto* (which   |
|                 | uses color if standard output/error refer to a     |
|                 | terminal).                                         |
|                 | Colors are set to ``[34m`` (blue foreground text)  |
|                 | for stdout and ``[31m`` (red foreground text) for  |
|                 | stderr, and cannot be modified.                    |
+-----------------+----------------------------------------------------+
| fd_max          | Maximum number of open file descriptors            |
|                 | permitted per ``clush`` process (soft resource     |
|                 | limit for open files). This limit can never exceed |
|                 | the system (hard) limit. The *fd_max* (soft) and   |
|                 | system (hard) limits should be high enough to      |
|                 | run ``clush``, although their values depend on     |
|                 | your fanout value.                                 |
+-----------------+----------------------------------------------------+
| history_size    | Set the maximum number of history entries saved in |
|                 | the GNU readline history list. Negative values     |
|                 | imply unlimited history file size.                 |
+-----------------+----------------------------------------------------+
| node_count      | Should ``clush`` display additional (node count)   |
|                 | information in buffer header? (yes/no)             |
+-----------------+----------------------------------------------------+
| maxrc           | Should ``clush`` return the largest of command     |
|                 | return codes? (yes/no)                             |
|                 | If set to no (the default), ``clush`` exit status  |
|                 | gives no information about command return codes,   |
|                 | but rather reports on ``clush`` execution itself   |
|                 | (zero indicating a successful run).                |
+-----------------+----------------------------------------------------+
| password_prompt | Enable password prompt and password forwarding to  |
|                 | stdin? (yes/no)                                    |
|                 | Generally used for specific                        |
|                 | :ref:`run modes <clush-modes>`, for example to     |
|                 | implement interactive *sudo(8)* support.           |
+-----------------+----------------------------------------------------+
| verbosity       | Set the verbosity level: 0 (quiet), 1 (default),   |
|                 | 2 (verbose) or more (debug).                       |
+-----------------+----------------------------------------------------+
| ssh_user        | Set the *ssh(1)* user to use for remote connection |
|                 | (default is to not specify).                       |
+-----------------+----------------------------------------------------+
| ssh_path        | Set the *ssh(1)* binary path to use for remote     |
|                 | connection (default is *ssh*).                     |
+-----------------+----------------------------------------------------+
| ssh_options     | Set additional (raw) options to pass to the        |
|                 | underlying *ssh(1)* command.                       |
+-----------------+----------------------------------------------------+
| scp_path        | Set the *scp(1)* binary path to use for remote     |
|                 | copy (default is *scp*).                           |
+-----------------+----------------------------------------------------+
| scp_options     | Set additional options to pass to the underlying   |
|                 | *scp(1)* command. If not specified, *ssh_options*  |
|                 | are used instead.                                  |
+-----------------+----------------------------------------------------+
| rsh_path        | Set the *rsh(1)* binary path to use for remote     |
|                 | connection (default is *rsh*). You could easily    |
|                 | use *mrsh* or *krsh* by simply changing this       |
|                 | value.                                             |
+-----------------+----------------------------------------------------+
| rcp_path        | Same as *rsh_path* but for rcp command (default is |
|                 | *rcp*).                                            |
+-----------------+----------------------------------------------------+
| rsh_options     | Set additional options to pass to the underlying   |
|                 | rsh/rcp command.                                   |
+-----------------+----------------------------------------------------+

.. _clushmode-config:

Run modes
^^^^^^^^^

Since version 1.9, ``clush`` has support for run modes, which are special
:ref:`clush-config` settings with a given name. Two run modes are provided in
example configuration files that can be copied and modified. They implement
password-based authentication with *sshpass(1)* and support of interactive
*sudo(8)* with password.

To use a run mode with ``clush --mode``, install a configuration file in one
of :ref:`clush-config`'s ``confdir`` (usually ``clush.conf.d``).  Only
configuration files ending in **.conf** are scanned. If the user running
``clush`` doesn't have read access to a configuration file, it is ignored.
When ``--mode`` is specified, you can display all available run modes for
the current user by enabling debug mode (``-d``).

Example of a run mode configuration file (e.g.
``/etc/clustershell/clush.conf.d/sudo.conf``) to add support for interactive
sudo::

    [mode:sudo]
    password_prompt: yes
    command_prefix: /usr/bin/sudo -S -p "''"

System administrators or users can easily create additional run modes by
adding configuration files to :ref:`clush-config`'s ``confdir``.

More details about using run modes can be found :ref:`here <clush-modes>`.

.. _groups-config:

Node groups
-----------

ClusterShell defines a *node group* syntax to represent a collection of nodes.
This is a convenient way to manipulate node sets, especially in HPC (High
Performance Computing) or with large server farms. This section explains how
to configure node group **sources**. Please see also :ref:`nodeset node groups
<nodeset-groups>` for specific usage examples.

.. _groups_config_conf:

groups.conf
^^^^^^^^^^^

ClusterShell loads *groups.conf* configuration files that define how to
obtain node groups configuration, i.e. the way the library should access
file-based or external node group **sources**.

The following configuration file defines system-wide default values for
*groups.conf*::

    /etc/clustershell/groups.conf

*groups.conf* settings might then be overridden (globally, or per user) if one
of the following files is found, in priority order::

    $XDG_CONFIG_HOME/clustershell/groups.conf
    $HOME/.config/clustershell/groups.conf (only if $XDG_CONFIG_HOME is not defined)
    {sys.prefix}/etc/clustershell/groups.conf
    $HOME/.local/etc/clustershell/groups.conf

.. note:: The path using `sys.prefix`_ was added in version 1.9.1 and is
   useful for Python virtual environments.

If the environment variable ``$CLUSTERSHELL_CFGDIR`` is defined, it replaces
``/etc/clustershell`` in the configuration file search path: the following
configuration file is used instead of ``/etc/clustershell/groups.conf`` (it
takes precedence over the files installed under `sys.prefix`_ and
``$HOME/.local``, and is only overridden by the per-user *groups.conf*), and
the ``$CFGDIR`` entries of *confdir* and *autodir* (see below) are expanded for
``$CLUSTERSHELL_CFGDIR`` instead of ``/etc/clustershell``::

    $CLUSTERSHELL_CFGDIR/groups.conf

This makes it possible for a user to have their own *node groups*
configuration. If no readable configuration file is found, group support will
be disabled but other node set operations will still work.

*groups.conf* defines configuration sub-directories, but may also define
group sources by itself. These **sources** provide external calls that are
detailed in :ref:`group-external-sources`.

The following example shows the content of a *groups.conf* file where node
groups are bound to the source named *genders* by default::

    [Main]
    default: genders
    confdir: $CFGDIR/groups.conf.d
    autodir: $CFGDIR/groups.d

    [genders]
    map: nodeattr -n $GROUP
    all: nodeattr -n ALL
    list: nodeattr -l

    [slurm]
    map: sinfo -h -o "%N" -p $GROUP
    all: sinfo -h -o "%N"
    list: sinfo -h -o "%P"
    reverse: sinfo -h -N -o "%P" -n $NODE

The *groups.conf* files are parsed with Python's `ConfigParser`_. The first
section whose name is *Main* accepts the settings described in the following
table.

+---------+------------------------------------------------------------+
| Key     | Value                                                      |
+=========+============================================================+
| default | **Name of the default group source.**                      |
|         |                                                            |
|         | Used when a group is specified without a source, e.g.      |
|         | ``@compute`` instead of ``@genders:compute``. Must be the  |
|         | name of an existing group source.                          |
+---------+------------------------------------------------------------+
| confdir | **Directories to search for .conf files that define        |
|         | additional group sources.**                                |
|         |                                                            |
|         | Each ``.conf`` file in these directories may define one or |
|         | more group source sections, as documented below. These     |
|         | sources are merged with the group sources defined in the   |
|         | main *groups.conf*. Duplicate group source sections within |
|         | the same directory are not allowed. Configuration files    |
|         | that are not readable by the current user are ignored      |
|         | (except the one that defines the default group source).    |
|         | Entries containing the variable ``$CFGDIR`` are expanded   |
|         | once for each configuration directory of the search path   |
|         | listed above (since version 1.11). The default *confdir*   |
|         | value enables both system-wide and any installed user      |
|         | configuration (thanks to ``$CFGDIR``). The key *groupsdir* |
|         | is accepted as an alias for *confdir*; if both are         |
|         | defined, *groupsdir* takes precedence.                     |
+---------+------------------------------------------------------------+
| autodir | **Directories to search for YAML group files.**            |
|         |                                                            |
|         | These files define node groups directly, without the need  |
|         | for external commands, and are parsed by the ClusterShell  |
|         | library itself, making them faster than upcall-based group |
|         | sources (see :ref:`group-file-based`). A single file may   |
|         | define multiple group sources. Entries containing the      |
|         | variable ``$CFGDIR`` are expanded once for each            |
|         | configuration directory of the search path listed above    |
|         | (since version 1.11). The default *autodir* value enables  |
|         | both system-wide and any installed user configuration      |
|         | (thanks to ``$CFGDIR``).                                   |
+---------+------------------------------------------------------------+

.. note:: Since version 1.11, ``$CFGDIR`` entries in *confdir* and *autodir*
   are expanded for **every** directory of the configuration file search path.
   Dropping a ``.conf`` file into
   ``$XDG_CONFIG_HOME/clustershell/groups.conf.d/`` (or a ``.yaml`` file into
   ``$XDG_CONFIG_HOME/clustershell/groups.d/``) is thus enough to add, or
   override, a group source without creating a user *groups.conf*.
   Configuration directories are scanned from the lowest to the highest
   priority and, within each directory, group sources are loaded from
   *groups.conf* sections first, then from *confdir*, then from *autodir*.
   When the same group source name is defined several times, the definition
   loaded last wins: a user drop-in file overrides a system-wide group source
   of the same name, and drop-in files override the *groups.conf* sections of
   the same directory (``nodeset -d`` or ``cluset -d`` shows such overrides).
   Entries of *confdir* and *autodir* without ``$CFGDIR`` are scanned along
   with the configuration directory of the file defining the option, and each
   directory is scanned only once.

Each following section, like `genders` and `slurm` in the example above,
defines a group source. The **map**, **mapall**, **all**, **list** and
**reverse** upcalls are explained below in :ref:`group-sources-upcalls`.

.. _group-file-based:

File-based group sources
^^^^^^^^^^^^^^^^^^^^^^^^

Version 1.7 introduces support for native handling of flat files with
different group sources to avoid the use of external upcalls for such static
configuration. This can be achieved through the *autodir* feature and YAML
files described below.

YAML group files
""""""""""""""""

Cluster node groups can be defined in straightforward YAML files. In such a
file, each YAML dictionary defines a group-to-nodes mapping. **Different
dictionaries** are handled as **different group sources**.

For compatibility reasons with previous versions of ClusterShell, this is not
the default way to define node groups yet. So here are the steps needed to try
this out:

Rename the following file::

    /etc/clustershell/groups.d/cluster.yaml.example

to a file having the **.yaml** extension, for example::

  /etc/clustershell/groups.d/cluster.yaml


Ensure that *autodir* is set in :ref:`groups_config_conf`::

  autodir: $CFGDIR/groups.d

In the following example, we also changed the default group source
to **roles** in :ref:`groups_config_conf` (the first dictionary defined in
the example), so that *@roles:groupname* can just be shortened to
*@groupname*.

.. highlight:: yaml

Here is an example of **/etc/clustershell/groups.d/cluster.yaml**::

    roles:
        adm: 'mgmt[1-2]'                 # define groups @roles:adm and @adm
        login: 'login[1-2]'
        compute: 'node[0001-0288]'
        gpu: 'node[0001-0008]'

        servers:                         # example of yaml list syntax for nodes
            - 'server001'                # in a group
            - 'server002,server101'                
            - 'server[003-006]'

        cpu_only: '@compute!@gpu'        # example of inline set operation
                                         # define group @cpu_only with node[0009-0288]

        storage: '@lustre:mds,@lustre:oss' # example of external source reference

        all: '@login,@compute,@storage'  # special group used for clush/nodeset -a
                                         # only needed if not including all groups

    lustre:
        mds: 'mds[1-4]'
        oss: 'oss[0-15]'
        rbh: 'rbh[1-2]'


If you wish to define an empty group (with no nodes), you can either use an
empty string ``''`` or any valid YAML null value (``null`` or ``~``).

.. note::

   To select **every node** of a group source, use the ``*`` wildcard, for
   example ``@lustre:*`` or, for the default source, ``@*``. This is the
   *all nodes* notation also used by ``clush -a`` and ``nodeset -a``, as
   described in :ref:`group-sources-upcalls`. The word ``all`` is not special:
   it is an ordinary group name, so ``@lustre:*`` and ``@lustre:all`` are
   **not** equivalent. ``@lustre:all`` resolves the group literally named
   ``all``, which yields an empty node set here because ``lustre`` defines no
   such group. By default *all nodes* is the union of every group in the
   source. Defining an optional ``all`` group, like the ``all:`` key shown
   above in the ``roles`` source, overrides that union for both ``-a`` and
   ``@source:*``.

.. highlight:: console

Testing the syntax of your group file can be quickly performed through the
``-L`` or ``--list-all`` command of :ref:`nodeset-tool`, doubled here as
``-LL`` to also display the nodes of each group::

    $ nodeset -LL
    @adm mgmt[1-2]
    @all login[1-2],mds[1-4],node[0001-0288],oss[0-15]
    @compute node[0001-0288]
    @cpu_only node[0009-0288]
    @gpu node[0001-0008]
    @login login[1-2]
    @servers server[001-006,101]
    @storage mds[1-4],oss[0-15]
    @lustre:mds mds[1-4]
    @lustre:oss oss[0-15]
    @lustre:rbh rbh[1-2]

.. _group-external-sources:

External group sources
^^^^^^^^^^^^^^^^^^^^^^

.. _group-sources-upcalls:

Group source upcalls
""""""""""""""""""""

Each node group source is defined by a section name (*source* name) and up to
five upcalls, described in the following table.

+---------+------------------------------------------------------------+
| Upcall  | Description                                                |
+=========+============================================================+
| map     | **Resolves a group name into a node set.**                 |
|         |                                                            |
|         | External shell command that should return a node set, list |
|         | of nodes or list of node sets (separated by space          |
|         | characters or by carriage returns). The variable *$GROUP*  |
|         | is replaced before executing the command. Either ``map``   |
|         | or ``mapall`` must be defined.                             |
+---------+------------------------------------------------------------+
| mapall  | **Returns all group-to-nodes mappings of the source in a   |
|         | single call.**                                             |
|         |                                                            |
|         | Optional external shell command that should print one      |
|         | ``group: nodes`` line per group. Useful when the source    |
|         | can dump all its groups at once (e.g. with ``sinfo`` or    |
|         | ``ansible-inventory --list``), as a single call then       |
|         | serves both ``map`` and ``list`` queries from the cache.   |
|         | ``mapall`` output takes precedence over the ``list``       |
|         | upcall. If ``map`` is also defined, it is used as a        |
|         | fallback for groups missing from the ``mapall`` output (or |
|         | all groups if caching is disabled); otherwise, missing     |
|         | groups resolve to an empty node set. The first ``:`` on    |
|         | each line separates the group name from the nodes, so      |
|         | group names must be single words without ``:``. Duplicate  |
|         | group lines are merged. A malformed output line makes the  |
|         | whole ``mapall`` call fail (nothing is cached and the next |
|         | query retries), and a failing ``mapall`` command does not  |
|         | fall back to ``map``.                                      |
+---------+------------------------------------------------------------+
| all     | **Returns all nodes of the group source.**                 |
|         |                                                            |
|         | Optional external shell command that should return a node  |
|         | set, list of nodes or list of node sets. If not specified, |
|         | the library will try to resolve all nodes by using the     |
|         | ``list`` external command in the same group source         |
|         | followed by ``map`` for each available group. The notion   |
|         | of *all nodes* is used by ``clush -a`` and also by the     |
|         | special group name ``@*`` (or ``@source:*``).              |
+---------+------------------------------------------------------------+
| list    | **Returns all group names of the source.**                 |
|         |                                                            |
|         | Optional external shell command that should return the     |
|         | group names (separated by space characters or by carriage  |
|         | returns). This upcall is not used when ``mapall`` is       |
|         | defined (unless caching is disabled), as the group list is |
|         | then derived from its output. If neither ``list`` nor      |
|         | ``mapall`` is specified, ClusterShell will not be able to  |
|         | list any available groups (e.g. with ``nodeset -l`` or     |
|         | ``cluset -l``), so it is highly recommended to set one of  |
|         | them.                                                      |
+---------+------------------------------------------------------------+
| reverse | **Finds the groups a single node belongs to.**             |
|         |                                                            |
|         | Optional external shell command. The variable *$NODE* is   |
|         | replaced before executing the command. If this external    |
|         | call is not specified, the reverse operation is computed   |
|         | in memory by the library from the ``list`` and ``map``     |
|         | external calls, if available. Also, if the number of nodes |
|         | to reverse is greater than the number of available groups, |
|         | the reverse external command is avoided automatically to   |
|         | reduce resolution time.                                    |
+---------+------------------------------------------------------------+

.. highlight:: ini

Example of a Slurm partition group source defined with a single **mapall**
upcall, instead of separate **map** and **list** upcalls::

    [slurmpart,sp]
    mapall: sinfo -h -o "%R:%N"

In addition to the context-dependent *$GROUP* and *$NODE* variables
described above, the following two variables are always available and also
replaced before executing shell commands:

* *$CFGDIR* is replaced by the directory of the configuration file the group
  source is defined in: a *confdir* directory for a group source defined in a
  ``.conf`` file, or the base directory of the (highest priority) *groups.conf*
  file defining its section otherwise
* *$SOURCE* is replaced by the current source name (see a usage example just
  below)

Upcall commands are executed with their standard input connected to
``/dev/null``, so they must not expect any input on stdin.

Group names must not contain any of the following characters: ``@,!&^*``.
Since version 1.11, a group name returned by a group source that contains such
a character is ignored (previous versions reported a fatal error). The command
line tools print a warning about ignored group names on standard error, unless
``-q`` is used; applications may retrieve them with
``GroupResolver.ignored_groups()``.

.. _group-external-caching:

Caching considerations
""""""""""""""""""""""

External command results are cached in memory, for a limited amount of time,
to avoid multiple similar calls.

The optional parameter **cache_time**, when specified within a group source
section, defines the number of seconds each upcall result is kept in cache,
in memory only. Please note that caching is actually only useful for
long-running programs (like daemons) that are using node groups, not for
one-shot commands like :ref:`clush <clush-tool>` or
:ref:`cluset <cluset-tool>`/:ref:`nodeset <nodeset-tool>`.

The default value of **cache_time** is 3600 seconds.

Multiple sources section
""""""""""""""""""""""""

.. highlight:: ini

Use a comma-separated list of source names in the section header if you want
to define multiple group sources with similar upcall commands. The special
variable ``$SOURCE`` is always replaced by the source name before command
execution (here `cluster`, `racks` and `cpu`), for example::

    [cluster,racks,cpu]
    map: get_nodes_from_source.sh $SOURCE $GROUP
    all: get_all_nodes_from_source.sh $SOURCE
    list: list_nodes_from_source.sh $SOURCE

is equivalent to::

    [cluster]
    map: get_nodes_from_source.sh cluster $GROUP
    all: get_all_nodes_from_source.sh cluster
    list: list_nodes_from_source.sh cluster

    [racks]
    map: get_nodes_from_source.sh racks $GROUP
    all: get_all_nodes_from_source.sh racks
    list: list_nodes_from_source.sh racks

    [cpu]
    map: get_nodes_from_source.sh cpu $GROUP
    all: get_all_nodes_from_source.sh cpu
    list: list_nodes_from_source.sh cpu

Return code of external calls
"""""""""""""""""""""""""""""

Each external command might return a non-zero return code when the operation
is not doable. But if the call returns zero, for instance for a non-existing
group, the user will not receive any error when trying to resolve such an
unknown group. The desired behavior is up to the system administrator.

.. _group-slurm-bindings:

Slurm group bindings
""""""""""""""""""""

Enable Slurm node group bindings by renaming the example configuration file
usually installed as ``/etc/clustershell/groups.conf.d/slurm.conf.example`` to
``slurm.conf``. Seven group sources are defined in this file and are detailed
below. Each section comes with a long and a short name (for convenience), but
both define the same group source.

While examples below are based on the :ref:`nodeset-tool` tool, all Python
tools using ClusterShell and the :class:`.NodeSet` class will automatically
benefit from these additional node groups.

.. highlight:: ini

The first section **slurmpart,sp** defines a group source based on Slurm
partitions. Each group is named after the partition name and contains the
partition's nodes::

    [slurmpart,sp]
    map: sinfo -h -o "%N" -p $GROUP
    mapall: sinfo -h -o "%R:%N"
    all: sinfo -h -o "%N"
    list: sinfo -h -o "%R"
    reverse: sinfo -h -N -o "%R" -n $NODE

.. highlight:: console

Example of use with :ref:`nodeset <nodeset-tool>` on a cluster having two Slurm
partitions named *kepler* and *pascal*::

    $ nodeset -s sp -ll
    @sp:kepler cluster-[0001-0065]
    @sp:pascal cluster-[0066-0068]

.. highlight:: ini

The second section **slurmresv,sr** defines a group source based on Slurm
reservations. Each group is based on a different reservation and contains
the nodes currently in that reservation::

    [slurmresv,sr]
    map: scontrol -o show reservation $GROUP | grep -Po 'Nodes=\K[^ ]+'
    mapall: scontrol -o show reservation | sed -n 's/^ReservationName=\([^ :]*\) .* Nodes=\([^ ]*\).*/\1:\2/p'
    all: scontrol -o show reservation | grep -Po 'Nodes=\K[^ ]+'
    list: scontrol -o show reservation | grep -Po 'ReservationName=\K[^ ]+'
    cache_time: 60

.. highlight:: console

Example of use on a cluster having a reservation in place for an upcoming
system maintenance::

    $ nodeset -s slurmresv -l
    @slurmresv:Maintenance_2025-02-04
    $ clush -w @slurmresv:Maintenance_2025-02-04 uptime

.. highlight:: ini

The next section **slurmstate,st** defines a group source based on Slurm
node states. Each group is based on a different state name and contains the
nodes currently in that state::

    [slurmstate,st]
    map: sinfo -h -o "%N" -t $GROUP
    mapall: sinfo -h -o "%T:%N" | sed 's/[*~#!%$@+^-]*:/:/'
    all: sinfo -h -o "%N"
    list: sinfo -h -o "%T" | tr -d '*~#$@+'
    reverse: sinfo -h -N -o "%T" -n $NODE | tr -d '*~#$@+'
    cache_time: 60

Here, :ref:`cache_time <group-external-caching>` is set to 60 seconds instead
of the default (3600s) to avoid caching results in memory for too long, in
case of state change (this is only useful for long-running processes, not
one-shot commands).

.. highlight:: console

Example of use with :ref:`nodeset <nodeset-tool>` to get the current nodes that
are in the Slurm state *drained*::

    $ nodeset -f @st:drained
    cluster-[0058,0067]

.. highlight:: ini

The next section **slurmjob,sj** defines a group source based on Slurm jobs.
Each group is based on a running job ID and contains the nodes currently
allocated for this job::

    [slurmjob,sj]
    map: squeue -h -j $GROUP -o "%N"
    mapall: squeue -h -o "%i:%N" -t R
    list: squeue -h -o "%i" -t R
    reverse: squeue -h -w $NODE -o "%i"
    cache_time: 60

The next section **slurmuser,su** defines a group source based on Slurm users.
Each group is based on a username and contains the nodes currently
allocated for jobs belonging to the username::

    [slurmuser,su]
    map: squeue -h -u $GROUP -o "%N" -t R
    mapall: squeue -h -o "%u:%N" -t R
    list: squeue -h -o "%u" -t R
    reverse: squeue -h -w $NODE -o "%i"
    cache_time: 60

.. highlight:: console

Example of use with :ref:`clush <clush-tool>` to execute a command on all nodes
with running jobs of username::

    $ clush -bw@su:username 'df -Ph /scratch'
    $ clush -bw@su:username 'du -s /scratch/username'

:ref:`cache_time <group-external-caching>` is also set to 60 seconds instead
of the default (3600s) to avoid caching results in memory for too long, because
this group source is likely very dynamic (this is only useful for long-running
processes, not one-shot commands).

.. highlight:: ini

The next section **slurmaccount,sa** defines a group source based on Slurm
accounts. Each group is based on an account and contains the nodes where there
are running jobs under this account::

    [slurmaccount,sa]
    map: squeue -h -A $GROUP -o "%N" -t R
    mapall: squeue -h -o "%a:%N" -t R
    list: squeue -h -o "%a" -t R
    reverse: squeue -h -w $NODE -o "%a" 2>/dev/null || true
    cache_time: 60

.. highlight:: console

For example, to find all nodes that have running jobs from the account ``ruthm``::

    $ cluset -f @sa:ruthm
    sh02-01n57,sh03-09n51,sh03-11n10

.. highlight:: ini

The next section **slurmqos,sq** defines a group source based on Slurm QoS.
Each group is based on a qos and contains the nodes where there are running
jobs under this qos::

    [slurmqos,sq]
    map: squeue -h -q $GROUP -o "%N" -t R
    mapall: squeue -h -o "%q:%N" -t R
    list: squeue -h -o "%q" -t R
    reverse: squeue -h -w $NODE -o "%q" 2>/dev/null || true
    cache_time: 60

.. highlight:: console

Then it is easy to find nodes currently running jobs in a specified qos, here
in qos ``long`` for example::

    $ cluset -f @slurmqos:long
    sh02-01n[01-02,16-17,45,51,56],sh03-01n[02,29,61]

.. _group-xcat-bindings:

xCAT group bindings
"""""""""""""""""""

Enable xCAT node group bindings by renaming the example configuration file
usually installed as ``/etc/clustershell/groups.conf.d/xcat.conf.example`` to
``xcat.conf``. A single group source is defined in this file and is detailed
below.

.. warning:: xCAT installs its own `nodeset`_ command which
   usually takes precedence over ClusterShell's :ref:`nodeset-tool` command.
   In that case, simply use :ref:`cluset <cluset-tool>` instead.

While examples below are based on the :ref:`cluset-tool` tool, all Python
tools using ClusterShell and the :class:`.NodeSet` class will automatically
benefit from these additional node groups.

.. highlight:: ini

The section **xcat** defines a group source based on xCAT static node groups::

    [xcat]

    # list the nodes in the specified node group
    map: lsdef -s -t node $GROUP | cut -d' ' -f1
    
    # list all the nodes defined in the xCAT tables
    all: lsdef -s -t node | cut -d' ' -f1
    
    # list all groups
    list: lsdef -t group | cut -d' ' -f1

.. highlight:: console

Example of use with :ref:`cluset-tool`::

    $ lsdef -s -t node dtn
    sh-dtn01  (node)
    sh-dtn02  (node)
    
    $ cluset -s xcat -f @dtn
    sh-dtn[01-02]

.. highlight:: text

.. _group-ansible-bindings:

Ansible inventory group bindings
"""""""""""""""""""""""""""""""""

Enable Ansible inventory group bindings by renaming the example configuration
file usually installed as
``/etc/clustershell/groups.conf.d/ansible.conf.example`` to ``ansible.conf``.

**Requirements**: ``ansible-core`` (provides the ``ansible-inventory`` command)
and ``jq``.

The section **ansible** defines a group source backed by Ansible inventory.
Each upcall command uses ``ANSIBLE_INVENTORY`` as an inline environment variable
prefix so that multiple inventory sources (comma-separated paths) are supported.
The default path defined in the configuration file is used as a fallback when
``$ANSIBLE_INVENTORY`` is not set in the environment::

    ANSIBLE_INVENTORY="${ANSIBLE_INVENTORY:-/path/to/inventory}" ansible-inventory --list ...

The example upcalls resolve hosts to their Ansible ``inventory_hostname`` rather
than the ``ansible_host`` connection address, so names from non-resolvable
aliases (e.g. with dynamic inventory) are not directly usable with
:ref:`clush-tool`. These commands can be adapted to your inventory as needed,
for instance to emit ``ansible_host`` instead.

Another common adaptation is to strip a DNS domain suffix when the inventory
contains fully qualified hostnames but short names resolve on the cluster.
Append ``| sub("\\.example\\.com$"; "")`` to the ``map`` and ``all`` filters,
and in ``mapall``, apply it to each hostname by changing ``[r($d;.)]`` to
``[r($d;.) | sub("\\.example\\.com$"; "")]``.

The ``mapall`` upcall resolves every group in a single ``ansible-inventory
--list`` call. As ``--list`` always dumps the whole inventory regardless of the
group being queried, this avoids running one ``ansible-inventory`` command per
group when listing or resolving several groups at once (e.g. ``nodeset -ll``).
Group names that contain ``:`` or whitespace cannot be expressed in the
``mapall`` output format; they are skipped from ``mapall`` and resolved through
the ``map`` upcall instead, so they still resolve but do not appear in
``nodeset -l`` output.

.. highlight:: console

Example of use with :ref:`nodeset-tool` on a cluster managed with Ansible::

    $ nodeset -s ansible -l
    @ansible:db
    @ansible:web
    @ansible:web_prod
    @ansible:web_test
    $ clush -w @ansible:web uptime

.. highlight:: text

.. _topology-config:

Tree topology
-------------

The optional topology configuration file defines the propagation routes used
by ClusterShell's :ref:`tree execution mode <clush-tree>` to reach target
nodes through gateway nodes. It is loaded from the same configuration
directories as the other ClusterShell configuration files, the system-wide
defaults being::

    /etc/clustershell/topology.yaml
    /etc/clustershell/topology.conf

Two file syntaxes are supported: YAML (*topology.yaml*, preferred since
version 1.11, requires the PyYAML module) and INI (*topology.conf*). When
both files are present at the same location, *topology.yaml* is used.

.. highlight:: yaml

In YAML, routes are declared as a list of route objects, each made of
``gateways`` and ``targets`` node sets::

    routes:
      - gateways: rio0
        targets:  rio[10-13]
      - gateways: rio[10-11]
        targets:  rio[100-240]
      - gateways: rio[12-13]
        targets:  rio[300-440]

The same ``gateways`` may be used in several routes, for example to reach
several distinct target groups through one gateway pool. Each target node
must however be reachable through a single route: two routes whose
``targets`` overlap are rejected, even when they share the same gateways.
:ref:`nodeset-groups` are supported as values but must be quoted, as a
leading ``@`` is a reserved YAML character (e.g. ``gateways: "@gw"``).

.. _topology-priorities:

Gateway priorities
^^^^^^^^^^^^^^^^^^

Since version 1.11, the ``gateways`` of a route may also be written as a
list of gateway entries with the following attributes:

- ``nodes``: gateway node set (required)
- ``weight``: relative share of the load among gateways of equal priority
  (integer >= 1, default 1)
- ``priority``: failover rank (integer >= 1, default 1); **a lower number
  means a higher priority**

Gateways of a given priority are used only when all gateways with a lower
priority number are unreachable: priority 1 gateways are the default,
priority 2 gateways are used when all priority 1 gateways are down, and
so on. Gateways of equal priority share the load using weighted
least-connections. For example, two gateways backing each other up, each
being the default for its own target group::

    routes:
      - gateways:
          - nodes: gw1
          - nodes: gw2
            priority: 2         # gw1 default, gw2 failover
        targets:  rio[100-199]
      - gateways:
          - nodes: gw2
          - nodes: gw1
            priority: 2         # gw2 default, gw1 failover
        targets:  rio[200-299]

``nodes`` may be any node set or node group, so a balanced gateway pair
with a spare used only when both are down is written::

    routes:
      - gateways:
          - nodes: gw[1-2]      # priority 1: load-balanced pair
          - nodes: gw3
            priority: 2         # priority 2: failover only
        targets:  rio[100-299]

Use ``weight`` to distribute the load proportionally between gateways of
equal priority::

    routes:
      - gateways:
          - nodes: gw[1-2]
            weight: 2           # twice the load of gw3
          - nodes: gw3
          - nodes: gw4
            priority: 2         # failover only
        targets:  rio[100-299]

A plain list of node sets, as in ``gateways: [gw1, gw2]``, is shorthand
for entries with default weight and priority: a load-shared pool
equivalent to ``gateways: gw[1-2]``. Failover is always explicit with
``priority``.

The ``nodes`` of the gateway entries of a route must not overlap: a gateway
cannot be both a default and a failover, nor carry two different weights.

.. note:: All gateways of a route must be able to reach the whole ``targets``
   node set of that route. Priorities select which gateway is preferred; they
   do not allow gateways with disjoint reach to back each other up.

.. note:: Failover is triggered at connection time: a gateway is considered
   unreachable when its channel cannot be established (there is no periodic
   health check). In a multi-level tree, gateways must also run ClusterShell
   1.11 or later for priorities to be applied at their own level.

INI syntax
^^^^^^^^^^

.. highlight:: ini

In INI, routes are declared under a ``[routes]`` section, one route per
line. This is the historical syntax and remains fully supported; unlike
YAML, a source node set may not be repeated and gateway priorities are
not available::

    [routes]
    rio0: rio[10-13]
    rio[10-11]: rio[100-240]
    rio[12-13]: rio[300-440]

.. highlight:: text

Example files are provided with ClusterShell as *topology.yaml.example* and
*topology.conf.example*. See :ref:`clush-tree` for a full description of tree
mode, including how routes are turned into a propagation tree and the related
command line options (such as ``--topology``).

.. _defaults-config:

Library Defaults
----------------

.. warning:: Modifying library defaults is for advanced users only as that
   could change the behavior of tools using ClusterShell. Moreover, tools are
   free to enforce their own defaults, so changing library defaults may not
   change a global behavior as expected.

Since version 1.7, most defaults of the ClusterShell library may be overridden
in *defaults.conf*.

The following configuration file defines ClusterShell system-wide defaults::

    /etc/clustershell/defaults.conf

*defaults.conf* settings might then be overridden (globally, or per user) if
one of the following files is found, in priority order::

    $XDG_CONFIG_HOME/clustershell/defaults.conf
    $HOME/.config/clustershell/defaults.conf (only if $XDG_CONFIG_HOME is not defined)
    {sys.prefix}/etc/clustershell/defaults.conf
    $HOME/.local/etc/clustershell/defaults.conf

If the environment variable ``$CLUSTERSHELL_CFGDIR`` is defined, the following
configuration file is used instead of ``/etc/clustershell/defaults.conf``; it
takes precedence over the files installed under `sys.prefix`_ and
``$HOME/.local``, and is only overridden by the per-user configuration file::

    $CLUSTERSHELL_CFGDIR/defaults.conf

Settings
^^^^^^^^

Library defaults are organized in sections, each of them covering a
particular ClusterShell subsystem. The following tables describe the
available settings, grouped by section.

The ``[task.default]`` section defines Task worker defaults.

+--------------------+----------------------------------------------------+
| Key                | Value                                              |
+====================+====================================================+
| stderr             | Whether to store stderr separately from stdout     |
|                    | (default: no).                                     |
+--------------------+----------------------------------------------------+
| stdin              | Whether to keep the command's standard input open  |
|                    | for writing (e.g. via ``Worker.write()``); if      |
|                    | disabled, EOF is sent at startup so commands that  |
|                    | read from stdin do not block (default: yes).       |
+--------------------+----------------------------------------------------+
| stdout_msgtree     | Whether to gather stdout in a message tree, as     |
|                    | required to display gathered output, e.g. with     |
|                    | ``clush -b`` (default: yes).                       |
+--------------------+----------------------------------------------------+
| stderr_msgtree     | Whether to gather stderr in a message tree         |
|                    | (default: yes).                                    |
+--------------------+----------------------------------------------------+
| engine             | Event engine backend: *auto*, *epoll*, *poll* or   |
|                    | *select* (default: *auto*). With *auto*, the best  |
|                    | available backend is selected: *epoll* first, then |
|                    | *poll*, then *select*. Overriding the default is   |
|                    | rarely needed and mostly useful for debugging.     |
+--------------------+----------------------------------------------------+
| port_qlimit        | Accepted here only for 1.8 compatibility; a        |
|                    | non-default value in the ``[engine]`` section      |
|                    | takes precedence.                                  |
+--------------------+----------------------------------------------------+
| auto_tree          | Whether to automatically enable                    |
|                    | :ref:`tree mode <clush-tree>` when a               |
|                    | :ref:`topology file <topology-config>` is found    |
|                    | (default: yes).                                    |
+--------------------+----------------------------------------------------+
| local_workername   | Name of the worker module used for local           |
|                    | execution (default: *exec*).                       |
+--------------------+----------------------------------------------------+
| distant_workername | Name of the worker module used for remote          |
|                    | execution (default: *ssh*; see the *rsh* use       |
|                    | case below).                                       |
+--------------------+----------------------------------------------------+

The ``[task.info]`` section defines Task runtime defaults.

+--------------------+----------------------------------------------------+
| Key                | Value                                              |
+====================+====================================================+
| debug              | Whether to enable library debugging output         |
|                    | (default: no).                                     |
+--------------------+----------------------------------------------------+
| fanout             | Size of the sliding window of connectors (e.g. max |
|                    | number of *ssh(1)* processes allowed to run at the |
|                    | same time) (default: 64).                          |
+--------------------+----------------------------------------------------+
| grooming_delay     | Delay in seconds during which gateways aggregate   |
|                    | identical output lines and return codes before     |
|                    | sending them back in batch (tree mode)             |
|                    | (default: 0.25).                                   |
+--------------------+----------------------------------------------------+
| connect_timeout    | Timeout in seconds to allow a connection to        |
|                    | establish; if set to 0, no timeout occurs          |
|                    | (default: 10).                                     |
+--------------------+----------------------------------------------------+
| command_timeout    | Timeout in seconds to allow a command to           |
|                    | complete; if set to 0, no timeout occurs           |
|                    | (default: 0).                                      |
+--------------------+----------------------------------------------------+

The ``[engine]`` section defines event engine defaults.

+--------------------+----------------------------------------------------+
| Key                | Value                                              |
+====================+====================================================+
| port_qlimit        | Maximum number of messages that can be queued on   |
|                    | an engine port, used for inter-thread task         |
|                    | messaging (default: 100). This is the preferred    |
|                    | section for this key; a non-default value here     |
|                    | takes precedence over ``[task.default]`` (kept     |
|                    | for 1.8 compatibility).                            |
+--------------------+----------------------------------------------------+

The ``[nodeset]`` section defines NodeSet defaults.

+--------------------+----------------------------------------------------+
| Key                | Value                                              |
+====================+====================================================+
| fold_axis          | Axis or axes along which nD node sets are folded   |
|                    | for display; empty by default, meaning that        |
|                    | folding is computed on all axes (see               |
|                    | :ref:`defaults-config-slurm`).                     |
+--------------------+----------------------------------------------------+

Use case: rsh
^^^^^^^^^^^^^^

If your cluster uses an rsh variant like ``mrsh`` or ``krsh``, you may want to
change it in the library defaults.

An example file is usually available in
``/usr/share/doc/clustershell-*/examples/defaults.conf-rsh`` and could be
copied to ``/etc/clustershell/defaults.conf`` or to an alternate path
described above. Basically, the change consists in defining an alternate
distant worker by Python module name as follows::

    [task.default]
    distant_workername: Rsh


.. _defaults-config-slurm:

Use case: Slurm
^^^^^^^^^^^^^^^

If your cluster naming scheme has multiple dimensions, as in ``node-93-02``, we
recommend that you disengage some nD folding when using Slurm, which is
currently unable to detect some multidimensional node indexes when not
explicitly enclosed with square brackets.

To do so, define ``fold_axis`` to -1 in the :ref:`defaults-config` so that nD
folding is only computed on the last axis (seems to work best with Slurm)::

    [nodeset]
    fold_axis: -1

That way, node sets computed by ClusterShell tools can be passed to Slurm
without error.

Since this only affects how node sets are folded for display, you may also fold
along a single axis per invocation with the ``--axis`` option of
:ref:`nodeset <nodeset-tool>`, :ref:`cluset <cluset-tool>` and
:ref:`clush <clush-axis>`, instead of setting ``fold_axis`` here.

.. _ConfigParser: https://docs.python.org/3/library/configparser.html
.. _nodeset: https://xcat-docs.readthedocs.io/en/stable/guides/admin-guides/references/man8/nodeset.8.html
.. _sys.prefix: https://docs.python.org/3/library/sys.html#sys.prefix
