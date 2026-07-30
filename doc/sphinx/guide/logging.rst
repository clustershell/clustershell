.. _library-logging:

Library logging
===============

.. highlight:: python

Logger namespace
----------------

ClusterShell uses the standard Python ``logging`` module. Each module logs
through a logger named after itself, below the top-level ``ClusterShell``
logger, for example ``ClusterShell.NodeUtils``, ``ClusterShell.Task`` or
``ClusterShell.Worker.Tree``.

Following the `Logging HOWTO recommendation for libraries
<https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library>`_,
ClusterShell never configures logging on behalf of your application: it only
adds a ``NullHandler`` to its top-level logger. Nothing is logged anywhere
until your application configures logging.

.. warning:: Since version 1.11, an application that does not configure
   logging no longer sees ClusterShell warnings and errors on standard error.
   Such messages were previously printed by the ``logging`` module handler of
   last resort. Configure logging as shown below to get them back.

.. _library-logging-enabling:

Enabling ClusterShell messages
------------------------------

The simplest way is to configure logging globally in your application::

    import logging

    logging.basicConfig(level=logging.WARNING)

To enable ClusterShell messages only, and leave the logging configuration of
the rest of your application untouched, add a handler to the ``ClusterShell``
logger instead::

    import logging

    handler = logging.StreamHandler()  # stderr
    handler.setFormatter(logging.Formatter('%(name)s: %(levelname)s: '
                                           '%(message)s'))

    logger = logging.getLogger('ClusterShell')
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

The same applies to a single module: use ``ClusterShell.NodeUtils`` to get
node group resolution messages only.

.. note:: Most ClusterShell log records are ``DEBUG`` ones written to
   troubleshoot the library itself. They are verbose and contain object
   representations and engine internals. Use ``WARNING`` and above to only get
   messages that report an actual problem.

The command-line tools configure logging themselves, so this does not affect
them: see the ``-d`` option of :ref:`clush <clush-tool>`,
:ref:`nodeset <nodeset-tool>` and :ref:`cluset <cluset-tool>`. In Tree mode,
gateways write their own log file, as described in
:ref:`clush-tree-debug`.
