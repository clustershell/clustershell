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
    $HOME/.clush.conf (deprecated, for 1.6 compatibility only)

.. note:: The path using `sys.prefix`_ was added in version 1.9.1 and is
   useful for Python virtual environments.

In addition, if the environment variable ``$CLUSTERSHELL_CFGDIR`` is defined and
valid, it will be used instead. In that case, the following configuration file
will be tried first for ``clush``::

    $CLUSTERSHELL_CFGDIR/clush.conf

Settings
""""""""

Settings that apply to all ``clush`` :ref:`run modes <clushmode-config>` are
contained within the ``[Main]`` section.

The following table describes available ``clush`` config file settings.

+-----------------+----------------------------------------------------+
| Key             | Value                                              |
+=================+====================================================+
| fanout          | Size of the sliding window of connectors (eg. max  |
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
|                 | current user are ignored. The variable `$CFGDIR`   |
|                 | is replaced by the path of the highest priority    |
|                 | configuration directory found (where *clush.conf*  |
|                 | resides). The default *confdir* value enables both |
|                 | system-wide and any installed user configuration   |
|                 | (thanks to `$CFGDIR`). Duplicate directory paths   |
|                 | are ignored.                                       |
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
| color           | Whether  to  use  ANSI  colors  to  surround node  |
|                 | or nodeset prefix/header with escape sequences to  |
|                 | display them in color on the terminal. Valid       |
|                 | arguments are *never*, *always* or *auto* (which   |
|                 | use color if standard output/error refer to a      |
|                 | terminal).                                         |
|                 | Colors are set to ``[34m`` (blue foreground text)  |
|                 | for stdout and ``[31m`` (red foreground text) for  |
|                 | stderr, and cannot be modified.                    |
+-----------------+----------------------------------------------------+
| fd_max          | Maximum  number  of  open  file descriptors        |
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

Example of a run mode configuration file (eg.
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
obtain node groups configuration, ie. the way the library should access
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

In addition, if the environment variable ``$CLUSTERSHELL_CFGDIR`` is defined and
valid, it will be used instead. In that case, the following configuration file
will be tried first for *groups.conf*::

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
    confdir: /etc/clustershell/groups.conf.d $CFGDIR/groups.conf.d
    autodir: /etc/clustershell/groups.d $CFGDIR/groups.d

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
|         | main *groups.conf*. Duplicate group source sections are    |
|         | not allowed in those files. Configuration files that are   |
|         | not readable by the current user are ignored (except the   |
|         | one that defines the default group source). The variable   |
|         | `$CFGDIR` is replaced by the path of the highest priority  |
|         | configuration directory found (where *groups.conf*         |
|         | resides). The default *confdir* value enables both         |
|         | system-wide and any installed user configuration (thanks   |
|         | to `$CFGDIR`). Duplicate directory paths are ignored. The  |
|         | key *groupsdir* is accepted as an alias for *confdir*; if  |
|         | both are defined, *groupsdir* takes precedence.            |
+---------+------------------------------------------------------------+
| autodir | **Directories to search for YAML group files.**            |
|         |                                                            |
|         | These files define node groups directly, without the need  |
|         | for external commands, and are parsed by the ClusterShell  |
|         | library itself, making them faster than upcall-based group |
|         | sources (see :ref:`group-file-based`). A single file may   |
|         | define multiple group sources. The variable `$CFGDIR` is   |
|         | replaced by the path of the highest priority configuration |
|         | directory found (where *groups.conf* resides). The default |
|         | *autodir* value enables both system-wide and any installed |
|         | user configuration (thanks to `$CFGDIR`). Duplicate        |
|         | directory paths are ignored.                               |
+---------+------------------------------------------------------------+

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

  autodir: /etc/clustershell/groups.d $CFGDIR/groups.d

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
``-L`` or ``--list-all`` command of :ref:`nodeset-tool`::

    $ nodeset -LL
    @adm mgmt[1-2]
    @all login[1-2],mds[1-4],node[0001-0288],oss[0-15],rbh[1-2]
    @compute node[0001-0288]
    @cpu_only node[0009-0288]
    @gpu node[0001-0008]
    @login login[1-2]
    @storage mds[1-4],oss[0-15],rbh[1-2]
    @sysgrp sysgrp[1-4]
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
    mapall: sinfo -h -o "%R: %N"

In addition to the context-dependent *$GROUP* and *$NODE* variables
described above, the following two variables are always available and also
replaced before executing shell commands:

* *$CFGDIR* is replaced by the *groups.conf* base directory path
* *$SOURCE* is replaced by the current source name (see a usage example just
  below)

Upcall commands are executed with their standard input connected to
``/dev/null``, so they must not expect any input on stdin.

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
variable `$SOURCE` is always replaced by the source name before command
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
``slurm.conf``. Three group sources are defined in this file and are detailed
below. Each section comes with a long and short names (for convenience), but
actually defines a same group source.

While examples below are based on the :ref:`nodeset-tool` tool, all Python
tools using ClusterShell and the :class:`.NodeSet`  class will automatically
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
accounts. Each group is based on a account and contains the nodes where there
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
tools using ClusterShell and the :class:`.NodeSet`  class will automatically
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

The optional *topology.conf* file defines the propagation routes used by
ClusterShell's :ref:`tree execution mode <clush-tree>` to reach target nodes
through gateway nodes. It is loaded from the same configuration directories as
the other ClusterShell configuration files, the system-wide default being::

    /etc/clustershell/topology.conf

.. highlight:: ini

Routes are declared under a ``[routes]`` section, for example::

    [routes]
    rio0: rio[10-13]
    rio[10-11]: rio[100-240]
    rio[12-13]: rio[300-440]

.. highlight:: text

An example file is provided with ClusterShell as *topology.conf.example*. See
:ref:`clush-tree` for a full description of tree mode, including how routes are
turned into a propagation tree and the related command line options (such as
``--topology``).

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

In addition, if the environment variable ``$CLUSTERSHELL_CFGDIR`` is defined and
valid, it will be used instead. In that case, the following configuration file
will be tried first for ClusterShell defaults::

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
|                    | required to display gathered output, eg. with      |
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
|                    | *topology.conf* file is found (default: yes).      |
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
| fanout             | Size of the sliding window of connectors (eg. max  |
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

If your cluster uses a rsh variant like ``mrsh`` or ``krsh``, you may want to
change it in the library defaults.

An example file is usually available in
``/usr/share/doc/clustershell-*/examples/defaults.conf-rsh`` and could be
copied to ``/etc/clustershell/defaults.conf`` or to an alternate path
described above. Basically, the change consists in defining an alternate
distant worker by Python module name as follow::

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

.. _ConfigParser: http://docs.python.org/library/configparser.html
.. _nodeset: https://xcat-docs.readthedocs.io/en/stable/guides/admin-guides/references/man8/nodeset.8.html
.. _sys.prefix: https://docs.python.org/3/library/sys.html#sys.prefix
