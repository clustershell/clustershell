.. highlight:: console

Installation
============

ClusterShell is distributed in several packages. On RedHat-like OS, we
recommend to use the RPM package (.rpm) distribution.

As system software for cluster, ClusterShell is primarily made for
system-wide installation to be used by system administrators. However,
changes have been made so that it's now possible to install it without
root access (see :ref:`install-pip-user`).

.. _install-requirements:

Requirements
------------

ClusterShell should work with any Unix [#]_ operating systems which provides
Python 2.7 or 3.x and OpenSSH or any compatible Secure Shell clients. It is
regularly tested with Python 3.7 up to Python 3.14.

.. warning:: While we are making our best effort to maintain Python 2
   compatibility in the ClusterShell 1.10 series, we no longer run tests for
   Python 2. Therefore, functionality on Python 2 is not guaranteed and may
   break without notice. The 1.10 series is expected to be the last to support
   Python 2; ClusterShell 1.11 will require Python 3. For the best experience
   and continued support, it is strongly recommended to use Python 3.

For instance, ClusterShell is known to work on the following operating systems:

* GNU/Linux

  * Red Hat Enterprise Linux 8 (Python 3.6)

  * Red Hat Enterprise Linux 9 (Python 3.9)

  * Red Hat Enterprise Linux 10 (Python 3.12)

  * Fedora 42 and above (Python 3.13+)

  * Debian 12 "bookworm" (Python 3.11)

  * Debian 13 "trixie" (Python 3.13)

  * Ubuntu 22.04 LTS (Python 3.10)

  * Ubuntu 24.04 LTS (Python 3.12)

* macOS (Python 3)

Distribution
------------

ClusterShell is an open-source project distributed under the GNU Lesser General
Public License version or later (`LGPL v2.1+`_), which means that many
possibilities are offered to the end user. Also, as a software library,
ClusterShell should remain easily available to everyone. Hopefully, packages are
currently available for Fedora Linux, RHEL (through EPEL repositories), Debian,
Arch Linux and more.

Red Hat Enterprise Linux
^^^^^^^^^^^^^^^^^^^^^^^^

ClusterShell packages are maintained on Extra Packages for Enterprise Linux
`EPEL`_ for Red Hat Enterprise Linux (RHEL) and its compatible spinoffs such
as `Alma Linux`_ and `Rocky Linux`_. ClusterShell is currently available on
EPEL 8, 9 and 10.


Install ClusterShell from EPEL
""""""""""""""""""""""""""""""

First you have to enable the EPEL repository. We recommend to download and
install the `EPEL`_ repository RPM package. On Alma Linux and Rocky Linux,
this can be easily done using the following command::

    $ dnf install epel-release

Then, install ClusterShell's library module and tools using the following
command::

    $ dnf install clustershell

The tools and the Python 3 library module are installed by default with
``clustershell``. If interested in the Python 3 library only, you can install
ClusterShell's Python 3 subpackage using the following command::

    $ dnf install python3-clustershell

Fedora
^^^^^^

ClusterShell is available in all Fedora releases currently maintained by the
Fedora Project.

Install ClusterShell from *Fedora Updates*
""""""""""""""""""""""""""""""""""""""""""

ClusterShell is part of Fedora, so it is really easy to install it with
``dnf``, although you have to keep the Fedora *updates* default repository.
The following command checks whether the packages are available on a Fedora
system::

    $ dnf list \*clustershell
    Available Packages
    clustershell.noarch                     1.9.3-6.fc43              updates
    python3-clustershell.noarch             1.9.3-6.fc43              updates

Then, install ClusterShell's library module and tools using the following
command::

    $ dnf install clustershell

If interested in the Python 3 library only, you can install ClusterShell's
Python 3 subpackage using the following command::

    $ dnf install python3-clustershell

Install ClusterShell from Fedora Updates Testing
""""""""""""""""""""""""""""""""""""""""""""""""

Recent releases of ClusterShell are first available through the
`Test Updates`_ repository of Fedora, then it is later pushed to the stable
*updates* repository. The following ``dnf`` command will also checks for
packages availability in the *updates-testing* repository::

    $ dnf list \*clustershell --enablerepo=updates-testing

To install, also add the ``--enablerepo=updates-testing`` option, for
instance::

    $ dnf install clustershell --enablerepo=updates-testing

openSUSE
^^^^^^^^

ClusterShell is available in openSUSE Tumbleweed (Factory) and Leap since 2017.

To install ClusterShell on openSUSE, use::

    $ zypper install clustershell

If interested in the Python 3 library only, you can install ClusterShell's
Python 3 subpackage using the following command::

    $ zypper install python3-clustershell

Debian
^^^^^^

ClusterShell is available in Debian **main** repository (since 2011).

To install it on Debian, simply use::

    $ apt-get install clustershell

You can get the latest version on::

* https://packages.debian.org/sid/clustershell


Ubuntu
^^^^^^

Like Debian, it is easy to get and install ClusterShell on Ubuntu (also with
``apt-get``). To do so, please first enable the **universe** repository:

* https://packages.ubuntu.com/clustershell

.. _install-python:

Installing ClusterShell the Python way
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning:: Installing ClusterShell as root using pip [#]_ is discouraged and
   can result in conflicting behaviour with the system package manager.  Use
   packages provided by your OS instead to install ClusterShell system-wide.

.. _install-pip-user:

Installing ClusterShell as user using pip
"""""""""""""""""""""""""""""""""""""""""

To install ClusterShell as a standard Python package using pip as an user::

    $ pip install --user ClusterShell

Or alternatively, using the source tarball::

    $ pip install --user ClusterShell-1.x.tar.gz

Then, you might need to update your ``PATH`` to easily use the :ref:`tools`,
and possibly set the ``PYTHONPATH`` environment variable to be able to import
the library, and finally ``MANPATH`` for the man pages::

    $ export PATH=$PATH:~/.local/bin
    $
    $ # Might also be needed:
    $ export PYTHONPATH=$PYTHONPATH:~/.local/lib
    $ export MANPATH=$MANPATH:$HOME/.local/share/man

.. note:: On macOS, ``pip install --user`` places the tools in
   ``~/Library/Python/3.x/bin`` instead of ``~/.local/bin``; adjust ``PATH``
   accordingly.

Configuration files are installed in ``~/.local/etc/clustershell`` and are
automatically loaded before system-wide ones (for more info about supported
user config files, please see the :ref:`clush-config` or :ref:`groups-config`
config sections).

.. _install-venv-pip:

Isolated environment using virtualenv and pip
"""""""""""""""""""""""""""""""""""""""""""""

It is possible to use virtual env (`venv`_) and pip to install ClusterShell
in an isolated environment::

    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install ClusterShell

.. note:: Scripts that import the ClusterShell library must run with the
   Python interpreter where ClusterShell is installed: use
   ``#!/usr/bin/python3`` with distribution packages or
   ``pip install --user``, or your virtual environment's interpreter
   (eg. ``#!/usr/bin/env python3`` with the environment activated).

.. _install-source:

Source
------

Current source is available through Git, use the following command to retrieve
the latest development version from the repository::

    $ git clone https://github.com/clustershell/clustershell.git


.. [#] Unix in the same sense of the *Availability: Unix* notes in the Python
   documentation
.. [#] pip is a tool for installing and managing Python packages, such as
   those found in the Python Package Index

.. _LGPL v2.1+: https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html
.. _Test Updates: https://fedoraproject.org/wiki/QA/Updates_Testing
.. _EPEL: https://fedoraproject.org/wiki/EPEL
.. _Alma Linux: https://almalinux.org/
.. _Rocky Linux: https://rockylinux.org/
.. _venv: https://docs.python.org/3/tutorial/venv.html
