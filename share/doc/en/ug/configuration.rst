*******************
Configuration Files
*******************

Introduction
============
NOC stores configuration in INI files in etc/ directory.

INI File Format
===============

Comment Lines
-------------
Lines starting with # sign considered comments and ignored
during processing

Example::

    # This is comment line.
    # And another comment

Sections
--------
INI file separated to sections. Each section starts with section name enclosed by brackets.

Example::

    [section1]
    ...
    [section2]
    ...
    [section3]
    ...

Configuration variables
-----------------------
Configuration variables are the part of the sections. Each variable
set by variable name and variable value divided by = sign.
Variable value can be omitted in case of empty value. Trailing spaces are discarded.

Example::

    [section1]
    var1 = value1
    empty_var =


*.conf and *.defaults
=====================
Each configuration consists of two files: .conf and .defaults ones.
.defaults contains default values. .defaults are the part
of distribution and can be altered by software upgrade.
You shall no edit .defaults directly, or your changes can be lost.
Edit .conf file instead. .conf contains site-specific settings.
Variables in .conf file override default values from .defaults.
If no variable set in .conf default value from .defaults used.

.. _noc-conf:

noc.conf
========
Stores global configuration

.. _noc-conf-main:

[main] section
--------------

.. _noc-conf-main-debug:

debug
^^^^^
**Boolean.**

true - display error reports in HTML page. false - send error report via email to admin_emails

.. _noc-conf-main-admin_emails:

admin_emails
^^^^^^^^^^^^
Comma-separated list of emails which will receive error_reports when debug = false

.. _noc-conf-main-timezone:

timezone
^^^^^^^^
Local time zone for installation. Choices can be found here: http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE although not all variations may be possible on all operating systems. If running in a Windows environment this must be set to the same as your system time zone.

.. _noc-conf-main-language_code:

language_code
^^^^^^^^^^^^^
Language code for installation. All choices can be found here: http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes http://blogs.law.harvard.edu/tech/stories/storyReader$15

.. _noc-conf-main-secret_key:

secret_key
^^^^^^^^^^
Random string used as seed for web session protection. Make this key unique and keep secret.

.. _noc-conf-main-server_email:

server_email
^^^^^^^^^^^^
From: field for all NOC-generated email

.. _noc-conf-database:

[database] section
------------------

.. _noc-conf-database-engine:
 
engine
------
Database engine. Only postgresql_psycopg2 supported at this moment.

.. _noc-conf-database-name:

name
----
Database name

.. _noc-conf-database-user:

user
----
Database user

.. _noc-conf-database-password:

password
--------
Database password, if required

.. _noc-conf-database-host:

host
----
Database host. Empty for local connection. Can be UNIX-socket path as well.

.. _noc-conf-database-port:

port
----
Database port, if not default

.. _noc-fcgi-conf:

noc-fcgi.conf
=============
Stores noc-fcgi daemon configuration

.. _noc-fcgi-conf-main:

[main] secttion
---------------

.. _noc-fcgi-conf-main-logfile:
 
logfile
-------
Log file path

.. _noc-fcgi-conf-main-loglevel:

loglevel
--------
logging level. One of: debug, info, warning, error, critical

.. _noc-fcgi-conf-main-pidfile:

pidfile
-------
Pid file path

.. _noc-fcgi-conf-fcgi:

[fcgi] section
--------------

.. _noc-fcgi-conf-fcgi-socket:

socket
------
Path to UNIX socket to communicate with HTTP server

.. _noc-fcgi-conf-fcgi-minspare:

minspare
--------
Minimum spare worker threads

.. _noc-fcgi-conf-fcgi-maxspare:

maxspare
--------
Maximum spare worker threads

.. _noc-fcgi-conf-fcgi-maxrequests:

maxrequests
-----------
Maximum requests processed by worker threads

.. _noc-fcgi-conf-fcgi-maxchildren:

maxchildren
-----------
Maximum worker threads

.. _noc-sae-conf:

noc-sae.conf
============
Service Activation Engine configuration.

.. _noc-sae-conf-main:

[main] section
--------------

.. _noc-sae-conf-main-logfile:

logfile
-------
Log file path

.. _noc-sae-conf-main-loglevel:

loglevel
--------
logging level. One of: debug, info, warning, error, critical

.. _noc-sae-conf-main-pidfile:

pidfile
-------
Pid file path

.. _noc-sae-conf-sae:

[sae] section
-------------

.. _noc-sae-conf-sae-listen:

listen
------
Listen for activator connections at address

.. _noc-sae-conf-sae-port:

port
----
Listen for activator connections at port

.. _noc-sae-conf-sae-refresh_event_filter:

refresh_event_filter
--------------------
Event filter expire time. Activators will refresh their event filters after this time

.. _noc-activator-conf:

noc-activator.conf
==================

Activator configuration

.. _noc-activator-conf-main:

[main] section
--------------

.. _noc-activator-conf-main-logfile:

logfile
-------
Log file path

.. _noc-activator-conf-main-loglevel:

loglevel
--------
logging level. One of: debug, info, warning, error, critical

.. _noc-activator-conf-main-pidfile:

pidfile
-------
Pid file path

.. _noc-activator-conf-activator:

[activator] section
-------------------

.. _noc-activator-conf-activator-name:

name
----
Activator name used for authentication

.. _noc-activator-conf-activator-listen_traps:

listen_traps
------------
IP address or interface name to listen for SNMP Traps. Empty to disable SNMP Trap collector

.. _noc-activator-conf-activator-listen_syslog:

listen_syslog
-------------
IP address or interface name to listen for syslog. Empty to disable syslog collector

.. _noc-activator-conf-activator-secret:

secret
------
Secret key used for digest authentication

.. _noc-activator-conf-activator-software_update:

software_update
---------------
* true - enable software update on connect.
* false - do not update software on connect

.. _noc-activator-conf-activator-max_pull_config:

max_pull_config
---------------
Maximum concurrent telnet/ssh sessions

.. _noc-activator-conf-sae:

[sae] section
-------------

.. _noc-activator-conf-sae-host:

host
----
SAE address

.. _noc-activator-conf-sae-port:

port
----
SAE port

.. _noc-activator-conf-sae-local_address:

local_address
-------------
Use specified address as source address for SAE connections. Leave empty to use default address.
