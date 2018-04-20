.. _install_source:

Installing from source
**********************

Installation directory
======================
NOC installed in ``/opt/noc/`` directory by default.

Required packages
=================

Python
------
Ensure Python 2.5 or later installed. Check your installed python version by::

    # python --version

**WARNING:** NOC is not compatible with Python 3

**WARNING:** Common installation troubles are caused by two versions of python installed in the system.
If your system have several versions of Python installed ensure you calling right version when installing
required packages, NOC and performing NOC maintenance. Please note, ``noc``, ``root`` users and daemon
environment may have different PATHs. Ensure you are calling proper Python version each case.

PostgreSQL
----------
8.2 or later required. Please install PostgreSQL according to your operation system requirements.

**WARNING:** Common installation troubles are caused by two versions of PostgreSQL installed in the system.
If your system have several versions of PostgreSQL installed ensure you calling and linking with right version when installing
required packages, NOC and performing NOC maintenance. Please note, ``noc``, ``root`` users and daemon
environment may have different PATHs and INCLUDE. Ensure you are calling proper PostgreSQL version each case.
 
setuptools
----------
`Setuptools <http://pypi.python.org/pypi/setuptools/>`_ is an extension to python distutils
which allows seamless installation for the rest of packages.

Install::

    # wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c9.tar.gz#md5=3864c01d9c719c8924c455714492295e
    # gzip -dc < setuptools-0.6c9.tar.gz | tar xf -
    # cd setuptools-0.6c9
    # python setup.py install

psycopg2
--------
`Psycopg2 <http://initd.org/>`_ is a PostgreSQL interface for Python. Version 2.0.5 or later required.

Install::

    # easy_install psycopg2

gmpy
----
`gmpy <http://gmpy.sourceforge.net/>`_ is an general multiprecision python library, used together with pycrypto.
Version 1.4 or later requred.

Install::

    # easy_install gmpy


pycrypto
--------
`pycrypto <http://pycrypto.org/>`_ is the Python Cryptography Toolkit. Version 2.3 or later required.

Install::

    # easy_install pycrypto


webserver
---------
Any FastCGI-capable HTTP server supported. Commonly user choices are:

    - lighttpd
    - nginx
    - apache
    
Please install webserver according to your operation system's requirements.

libsmi
------
`libsmi <http://www.ibr.cs.tu-bs.de/projects/libsmi/>`_ is a library and collection of tools to access SMI/SNMP MIB Information.
Please install libsmi according to your operation system's requirements.

Mercurial
---------
Distributed version control system. Required to fetch updates from repository. Mercurial also is a default
format of Configuration Management repository. Mercurial 1.3 or later required.
Please install mercurial according to your operation system's requirements.

fping
-----
`fping <http://fping.sourceforge.net/>`_ is a tool to perform parralel ICMP host checking. fping is used by Fault Management module
to check Managed Objects availability. Install fping according to your operation system's requirements.

Optional Packages
=================

netifaces
---------
`netifaces <http://alastairs-place.net/netifaces/>`_ is a Python module to get interface IP addresses.
netifaces allows to write interface names instead of IP addresses in configs

Install::

    # easy_install netifaces

Getting NOC
===========
NOC sources can be obtained via source archive download or from mercurial repository.
Preferred way is to perform checkout from mercurial repo.

Checkout from mercurial repo
----------------------------
Checkout from mercurial repo is a best way to stay on bleeding edge of fresh updates. You
need mercurial to perform checkout and further update.

To fetch latest updates available::

    # hg clone http://hg.nocproject.org/noc noc

To fetch particular release (0.4 in example)::

    # hg clone -r 0.4 http://hg.nocproject.org/noc noc

Source Archive
--------------
Download latest source archive from http://redmine.nocproject.org/projects/noc/files and extract it::
    
    # gzip -dc noc-<version>.tgz | tar xf -
    
System Users and Groups
=======================
All noc files except ``/opt/noc/local`` and ``/opt/noc/static/doc`` directories must be owned by ``root``.
All noc daemons are running from ``noc`` user. Create ``noc`` user and group before continuing installation::

    # groupadd noc
    # useradd -g noc -s /bin/sh -d /home/noc noc

Installing NOC
==============
Go to unpacked NOC source distribution as ``root`` user and install NOC::

    # cd noc-<version>
    # python setup.py install

NOC will be installed into ``/opt/noc/`` directory. Finish your installation by::

    # cd /opt/noc
    # ./scripts/post-install

``post-install`` script will create required additional directories, set up permissions,
create configuration files and set up paths.

Create database
===============
Create database user ``noc`` from PostgreSQL superuser (``pgsql`` in example)::

    # su - pgsql
    pgsql@/$ createuser noc
    Shall the new role be a superuser? (y/n) n
    Shall the new role be allowed to create databases? (y/n) n
    Shall the new role be allowed to create more new roles? (y/n) n

Then create database ``noc`` owned by user ``noc``::
    
    $ createdb -EUTF8 -Onoc noc
    
Change configuration files
==========================
Set up ``etc/noc.conf:[database]`` section. 

.. _installation_init_database:

Initialize database
===================
Initialize database, Fault Management rules and online documentation by::

    # su - noc
    noc@/$ cd /opt/noc
    noc@/opt/noc$ ./scripts/post-update

During intialization you will be prompted to create first NOC database superuser.
Enter superuser's name, password and email.
