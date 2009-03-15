*******************
Configuration Files
*******************

Introduction
============
NOC stores configuration in INI files in etc/ directory.

INI File Format
===============
Comments
--------
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
---------------------
Each configuration consists of two files: .conf and .defaults ones.
.defaults contains default values. .defaults are the part
of distribution and can be altered by software upgrade.
You shall no edit .defaults directly, or your changes can be lost.
Edit .conf file instead. .conf contains site-specific settings.
Variables in .conf file override default values from .defaults.
If no variable set in .conf default value from .defaults used.

noc.conf
--------
Stores global configuration

[main] section
^^^^^^^^^^^^^^

 * debug - Boolean. [BR]true - display error reports in HTML page. false - send error report via email to admin_emails
 * admin_emails - Comma-separated list of emails which will receive error_reports when debug = false
 * timezone - Local time zone for installation. Choices can be found here: http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE although not all variations may be possible on all operating systems. If running in a Windows environment this must be set to the same as your system time zone.
 * language_code - Language code for installation. All choices can be found here: http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes http://blogs.law.harvard.edu/tech/stories/storyReader$15
 * secret_key - Random string used as seed for web session protection. Make this key unique and keep secret.
 * server_email - From: field for all NOC-generated email
 
[database] section
^^^^^^^^^^^^^^^^^^
 
 * engine - Database engine. Only postgresql_psycopg2 supported at this moment.
 * name - Database name
 * user - Database user
 * password - Database password, if required
 * host - Database host. Empty for local connection. Can be UNIX-socket path as well.
 * port - Database port, if not default

noc-fcgi.conf
-------------
Stores noc-fcgi daemon configuration

[main] secttion
^^^^^^^^^^^^^^^
 
* logfile - Log file path
* loglevel - logging level. One of: debug, info, warning, error, critical
* pidfile - Pid file path

[fcgi] section
^^^^^^^^^^^^^^
 
* socket - Path to UNIX socket to communicate with HTTP server
* minspare - Minimum spare worker threads
* maxspare - Maximum spare worker threads
* maxrequests - Maximum requests processed by worker threads
* maxchildren - Maximum worker threads

noc-sae.conf
------------
Service Activation Engine configuration.

[main] section
^^^^^^^^^^^^^^
 
* logfile - Log file path
* loglevel - logging level. One of: debug, info, warning, error, critical
* pidfile - Pid file path

[sae] section
^^^^^^^^^^^^^

* listen - Listen for activator connections at address
* port - Listen for activator connections at port
* refresh_event_filter - Event filter expire time. Activators will refresh their event filters after this time

noc-activator.conf
------------------

Activator configuration
[main] section
^^^^^^^^^^^^^^

* logfile - Log file path
* loglevel - logging level. One of: debug, info, warning, error, critical
* pidfile - Pid file path

[activator] section
^^^^^^^^^^^^^^^^^^^

* name - Activator name used for authentication
* listen_traps - Enables SNMP trap collector at the specified address
* listen_syslog - Enables syslog collector at the specified address 
* secret - Secret key used for digest authentication
* software_update - true - enable software update on connect. false - do not update
* max_pull_config - Maximum concurrent telnet/ssh sessions

[sae] section
^^^^^^^^^^^^^
* host - SAE address
* port - SAE port
* local_address - Source address for SAE connections
