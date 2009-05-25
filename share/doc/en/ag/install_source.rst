**********************
Installing from source
**********************

Installing required and optional packages
=========================================

Required packages
-----------------
Python
^^^^^^

Ensure python 2.5 or later installed. Check your installed python version by::

    # python --version

**WARNING:** Python 3.0 or later is virtually another language. NOC and most required packages
are not compatible with Python 3

**WARNING:** Common installation troubles are caused by two versions of python installed in the system.
If your system have several versions of Python installed ensure you calling right version when installing
required packages, NOC and performing NOC maintenance. Please note, ``noc``, ``root`` users and daemon
environment may have different PATHs. Ensure you are calling proper Python version each case.

PostgreSQL
^^^^^^^^^^
8.1 or later required. Please install PostgreSQL according to your operation system requirements.

**WARNING:** Common installation troubles are causedby two versions of PostgreSQL installed in the system.
If your system have several versions of PostgreSQL installed ensure you calling and linking with right version when installing
required packages, NOC and performing NOC maintenance. Please note, ``noc``, ``root`` users and daemon
environment may have different PATHs. Ensure you are calling proper PostgreSQL version each case.
 
setuptools
^^^^^^^^^^
`Setuptools <http://pypi.python.org/pypi/setuptools/>`_ is an extension to python distutils
which allows seamless installation for the rest of packages.

Install::

    # wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c9.tar.gz#md5=3864c01d9c719c8924c455714492295e
    # gzip -dc < setuptools-0.6c9.tar.gz | tar xf -
    # cd setuptools-0.6c9
    # python setup.py install

psycopg2
^^^^^^^^
`Psycopg2 <http://initd.org/>`_ is a PostgreSQL interface for Python. Version 2.0.5 or later required.

Install::

    # easy_install psycopg2

Django
^^^^^^
`Django <http://www.djangoproject.org/ Django>`_ is a Python-based web framework actively used by NOC.
Version 1.0.2 or later required.

Install::

    # easy_install Django

Verify Django's version::

    # python
    Python 2.5.4 (r254:67916, Feb 17 2009, 20:16:45) 
    [GCC 4.3.3] on linux2 
    Type "help", "copyright", "credits" or "license" for more information. 
    >>> import django 
    >>> django.VERSION 
    (1, 0, 2, 'final', 0) 
     >>>

South
^^^^^
`South <http://south.aeracode.org/>`_ is an intillegent Django scheme migration tool.
Version 0.4 or later required.

Install::

    # easy_install South

protobuf
^^^^^^^^
`Protocol Buffers <http://code.google.com/p/protobuf/>`_ is compact Google's data interchange format,
used for internal RPC between SAE and Activators.

Install::
    
    # easy_install protobuf

Sphinx
^^^^^^
Python documentation tool required to rebuild online documentation. Install::

    # easy_install Sphinx

flup
^^^^
Required to run NOC web daemon in FastCGI mode. Install::

    # easy_install flup

webserver
^^^^^^^^^
Any FastCGI-capable HTTP server supported. Commonly user choices are:
* lighttpd
* apache
Please install webserver according to your operation system's requirements.


libsmi
^^^^^^
`libsmi <http://www.ibr.cs.tu-bs.de/projects/libsmi/>`_ is a library and collection of tools to access SMI/SNMP MIB Information.
Please install libsmi according to your operation system's requirements.

python-creole
^^^^^^^^^^^^^
`python-creole <http://code.google.com/p/python-creole/>`_ is a Creole parser implemented in pure python. Required to render
Creole articles in Knowledge Base. Install::

    # easy_install python-creole

Optional Packages
-----------------
Mercurial
^^^^^^^^^
Distributed version control system. Required to fetch updates from repository. Mercurial also is a default
format of Configuration Management repository.

pysnmp4
^^^^^^^
`pysnmp <http://pysnmp.sourceforge.net/>`_ is and pure-python implementation of SNMP v1/v2c/v3 protocol stack.
pysnmp4 together with pyasn1 are required for Fault Management module.

Install::

    # easy_install pysnmp

pyasn1
^^^^^^
`pyasn1 <http://pyasn1.sf.net/>`_ is a pure-Python implementation of ASN.1 types and codecs. pyasn1 together with
pysnmp4 are required for Fault Management module.

Install::

    # easy_install pyasn1

netifaces
^^^^^^^^^
`netifaces <http://alastairs-place.net/netifaces/>`_ is a Python module to get interface IP addresses.
netifaces allows to write interface names instead of IP addresses in configs

Install::

    # easy_install netifaces

fping
^^^^^
`fping <http://fping.sourceforge.net/>`_ is a tool to perform parralel ICMP host checking. fping is used by Fault Management module
to check Managed Objects availability. Install fping according to your operation system's requirements.

rsync
^^^^^
`rsync <http://samba.anu.edu.au/rsync/>`_ is an incremental file transfer tool widely used in DNS provisioning module. Install rsync
fping according to your operation system's requirements.

Getting NOC
===========
NOC sources can be obtained via source archive download or from mercurial repository

Source Archive
--------------
Download latest source archive from http://trac.nocproject.org/trac/downloads and extract it::
    
    # gzip -dc noc-<version>.tgz | tar xf -
    
Checkout from mercurial repo
----------------------------
Checkout from mercurial repo is a best way to stay on bleeding edge of fresh updates. You
need mercurial to perform checkout and further update.

To fetch latest updates available::

    # hg clone http://hg.nocproject.org/noc noc

To fetch particular release (0.1.6 in example)::

    # hg clone -r 0.1.6 http://hg.nocproject.org/noc noc

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
