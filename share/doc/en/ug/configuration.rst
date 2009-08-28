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


.conf and .defaults
=====================
Each configuration consists of two files: .conf and .defaults ones.
.defaults contains default values. .defaults are the part
of distribution and can be altered by software upgrade.
You shall no edit .defaults directly, or your changes can be lost.
Edit .conf file instead. .conf contains site-specific settings.
Variables in .conf file override default values from .defaults.
If no variable set in .conf default value from .defaults used.

Editing configuration files
===========================
Configuration files can be edited directly via text editor or using
Main > Setup > Config form

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

.. _noc-conf-main-server_email:

server_email
^^^^^^^^^^^^
From: field for all NOC-generated email

.. _noc-conf-main-admin_emails:

admin_emails
^^^^^^^^^^^^
Comma-separated list of emails which will receive error_reports when :ref:`noc-conf-main-debug` option set to *false*

.. _noc-conf-main-timezone:

timezone
^^^^^^^^
Local time zone for installation. Choices can be found here: `PostgreSQL DATETIME-TIMEZONE <http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE>`_ although not all variations may be possible on all operating systems. If running in a Windows environment this must be set to the same as your system time zone.

.. _noc-conf-main-language_code:

language_code
^^^^^^^^^^^^^
Language code for installation. All choices can be found here: `w3.org <http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes>`_

.. _noc-conf-main-secret_key:

secret_key
^^^^^^^^^^
Random string used as seed for web session protection. Make this key unique and keep secret.

.. _noc-conf-main-date_format:

date_format
^^^^^^^^^^^
Default date format to be used by noc. See :ref:`datetime_format` for format characters description.

.. _noc-conf-main-time_format:

time_format
^^^^^^^^^^^
Default time format to be used by noc. See :ref:`datetime_format` for format characters description.

.. _noc-conf-main-month_day_format:

month_day_format
^^^^^^^^^^^^^^^^
Default month and day format to be used by noc. See :ref:`datetime_format` for format characters description.

.. _noc-conf-main-year_month_format:

year_month_format
^^^^^^^^^^^^^^^^^
Default year and month format to be used by noc. See :ref:`datetime_format` for format characters description.

.. _noc-conf-main-datetime_format:

datetime_format
^^^^^^^^^^^^^^^
Default date and time format to be used by noc. See :ref:`datetime_format` for format characters description.

.. _noc-conf-main-installed_apps:

installed_apps
^^^^^^^^^^^^^^
Comma-separated list of locally installed django applications

.. _noc-conf-database:

[database] section
------------------

.. _noc-conf-database-engine:
 
engine
^^^^^^
Database engine. Only postgresql_psycopg2 supported at this moment.

.. _noc-conf-database-name:

name
^^^^
Database name

.. _noc-conf-database-user:

user
^^^^
Database user

.. _noc-conf-database-password:

password
^^^^^^^^
Database password, if required

.. _noc-conf-database-host:

host
^^^^
Database host. Empty for local connection. Can be UNIX-socket path as well.

.. _noc-conf-database-port:

port
^^^^
Database port, if not default

.. _noc-conf-customization:

customization section
---------------------

.. _noc-conf-customization-installation_name:

installation_name
^^^^^^^^^^^^^^^^^
The name of the NOC installation. Installation name shown at the top-left corner of the web interface.

.. _noc-conf-customization-logo_url:

logo_url
^^^^^^^^
Absolute or relative url of the logo. Logo is an image shown at the top-left corner of the web interface

.. _noc-conf-customization-logo_height:

logo_height
^^^^^^^^^^^
A height of the logo in pixels

.. _noc-conf-customization-logo_width:

logo_width
^^^^^^^^^^
A width of the logo in pixels

.. _noc-conf-path:

path section
------------

.. _noc-conf-path-backup_dir:

backup_dir
^^^^^^^^^^
Directory to place database and repo backup. Must be writable by *noc* user. Ensure *backup_dir* is readable and
writable only by trusted users

.. _noc-conf-path-ssh:

ssh
^^^
A path to the *ssh* binary

.. _noc-conf-path-telnet:

telnet
^^^^^^
A path to the *telnet* binary

.. _noc-conf-path-tar:

tar
^^^
A path to the *tar* binary. POSIX-compatible *tar* required. Additional extensions (like *z* flag) are not necessary

.. _noc-conf-path-gzip:

gzip
^^^^
A path to the *gzip* binary

.. _noc-conf-path-rsync:

rsync
^^^^^
A path to the *rsync* binary

.. _noc-conf-path-dig:

dig
^^^
A path to the *dig* binary

.. _noc-conf-path-pg_dump:

pg_dump
^^^^^^^
A path to the PostgreSQL *pg_dump* utility. Ensure proper version of *pg_dump* used (PostgreSQL 8.1 or later)

.. _noc-conf-path-smilint:

smilint
^^^^^^^
A path to the *smilint* utility. *smilint* is a part of *libsmi* distribution

.. _noc-conf-path-smidump:

smidump
^^^^^^^
A path to the *smidump* utility. *smidump* is a part of *libsmi* distribution

.. _noc-conf-path-gpg:

gpg
^^^
A path to GnuPG binary.

.. _noc-conf-cm:

cm section
----------
This section describes configuration management settings

.. _noc-conf-cm-repo:

repo
^^^^
Path to the repository. *repo* must be writable by *noc* user. Ensure *backup_dir* is readable and
writable only by trusted users

.. _noc-conf-cm-vcs_type:

vcs_type
^^^^^^^^
A type of Version Control System (VCS) used by cm. Available types are

=== ==============================
hg  Mercurial, stable, recommended
CSV CVS, experimental
=== ==============================

.. _noc-conf-cm-vcs_path:

vcs_path
^^^^^^^^
A path to VCS utility binary (hg, CVS, etc)

.. _noc-conf-cm-timeout_variation:

timeout_variation
^^^^^^^^^^^^^^^^^
Random *variation* of timeout. *Variation* is necessary to perform *local task reordering* to prevent constant
queue blocking by improperly functioning managed objects. *Variation* is defined in percents. When timeout is
T seconds and variation is V percents real timeout will be calculated as equally distributed random value
in interval [T*(1-V/100),T*(1+V/100)]

.. _noc-conf-cm-timeout_error:

timeout_error
^^^^^^^^^^^^^
Timeout to wait when error occured during get_config script execution

.. _noc-conf-cm-timeout_overload:

timeout_overload
^^^^^^^^^^^^^^^^
Timeout to wait when activator reports overload during get_config script execution. Activator *overload* means
activator's amount of concurrently executing scripts exceeds :ref:`noc-activator-conf-activator-max_pull_config` value

.. _noc-conf-cm-timeout_down:

timeout_down
^^^^^^^^^^^^
Timeout to wait when activator reports target host is down. Target host reachability status updated every time
ping probe executed

.. _noc-conf-peer:

[peer] section
--------------

.. _noc-conf-peer-rpsl_inverse_pref_style:

rpsl_inverse_pref_style
^^^^^^^^^^^^^^^^^^^^^^^
Select RPSL pref= behavior. *off* means pref = localpref, *on* means standard RPSL's pref = 65535-localpref

.. _noc-conf-dns:

[dns] section
-------------

.. _noc-conf-dns-warn_before_expired_days:

warn_before_expired_days
^^^^^^^^^^^^^^^^^^^^^^^^
Start to issue domain expiration warnings from *warn_before_expired_days* day before deadline

.. _noc-conf-tt:

tt section
----------
Trouble-ticketing system integration.

.. _noc-conf-tt-url:

url
^^^
Pattern to convert trouble ticket id to the link URL. Following strings are expanded to:

====== =================================
string description
%(tt)s Expanded to the trouble ticket id
====== =================================

.. _noc-conf-xmlrpc:

xmlrpc section
--------------
XML-RPC server is a part of SAE. *xmlrpc* section describes *client* settings used to connect SAE via XML-RPC.

.. _noc-conf-xmlrpc-server:

server
^^^^^^
IP address of the SAE

.. _noc-conf-xmlrpc-port:

port
^^^^
Port used by XML-RPC interface

.. _noc-conf-backup:

[backup] section
----------------
[backup] section contains settings for main.backup periodic task

.. _noc-conf-backup-keep_days:

keep_days
^^^^^^^^^
Keep last *keep_days* days of backups

.. _noc-conf-backup-keep_weeks:

keep_weeks
^^^^^^^^^^
After *keep_days* store only one backup per week for the next *keep_weeks* weeks.
Only backups created at *keep_day_of_week* day of week are left.

.. _noc-conf-backup-keep_day_of_week:

keep_day_of_week
^^^^^^^^^^^^^^^^
Keep only backup performed at *keep_day_of_week* (0 - Monday, 6 - Saturday)

.. _noc-conf-backup-keep_months:

keep_months
^^^^^^^^^^^
After *keep_weeks* interval expired keep only one backup per month for the next
*keep_months* months. Only backups created at *keep_day_of_months* days of months
are left.

.. _noc-conf-backup-keep_day_of_month:

keep_day_of_month
^^^^^^^^^^^^^^^^^
Keep only backups performed at *keep_day_of_month* (1-based)

.. _noc-conf-pgp:

[pgp] section
-------------

.. _noc-conf-pgp-use_key:

use_key
^^^^^^^
Private key used to encrypt message. Must me email or key id.

.. _noc-conf-pgp-keyserver:

keyserver
^^^^^^^^^
Keyserver used to retrieve missed keys

.. _noc-launcher-conf:

noc-launcher.conf
=================

.. _noc-launcher-conf-main:

[main] section
--------------

.. _noc-launcher-conf-main-logfile:
 
logfile
^^^^^^^
Log file path

.. _noc-launcher-conf-main-loglevel:

loglevel
^^^^^^^^
logging level. One of: debug, info, warning, error, critical

.. _noc-launcher-conf-main-logsize:

logsize
^^^^^^^
Maximum log file size in bytes. 0 (default) means unlimited size

.. _noc-launcher-conf-main-logfiles:

logfiles
^^^^^^^^
Keep *logfiles* backup copies of log file

.. _noc-launcher-conf-main-pidfile:

pidfile
^^^^^^^
Pid file path

.. _noc-launcher-conf-noc-fcgi:

[noc-fcgi] section
------------------

.. _noc-launcher-conf-noc-fcgi-enabled:

enabled
^^^^^^^
true/false. Launch noc-fcgi daemon

.. _noc-launcher-conf-noc-fcgi-user:

user
^^^^
Run noc-fcgi daemon with *user* credentials

.. _noc-launcher-conf-noc-fcgi-group:

group
^^^^^
Run noc-fcgi daemon with *group* credentials

.. _noc-launcher-conf-noc-sae:

[noc-sae] section
------------------

.. _noc-launcher-conf-noc-sae-enabled:

enabled
^^^^^^^
true/false. Launch noc-sae daemon

.. _noc-launcher-conf-noc-sae-user:

user
^^^^
Run noc-sae daemon with *user* credentials

.. _noc-launcher-conf-noc-sae-group:

group
^^^^^
Run noc-sae daemon with *group* credentials

.. _noc-launcher-conf-noc-notifier:

[noc-notifier] section
----------------------

.. _noc-launcher-conf-noc-notifier-enabled:

enabled
^^^^^^^
true/false. Launch noc-notifier daemon

.. _noc-launcher-conf-noc-notifier-user:

user
^^^^
Run noc-notifier daemon with *user* credentials

.. _noc-launcher-conf-noc-notifier-group:

group
^^^^^
Run noc-notifier daemon with *group* credentials

.. _noc-launcher-conf-noc-activator:


[noc-activator] section
-----------------------

.. _noc-launcher-conf-noc-activator-enabled:

enabled
^^^^^^^
true/false. Launch noc-activator daemon

.. _noc-launcher-conf-noc-activator-user:

user
^^^^
Run noc-activator daemon with *user* credentials

.. _noc-launcher-conf-noc-activator-group:

group
^^^^^
Run noc-activator daemon with *group* credentials

.. _noc-launcher-conf-noc-classifier:

[noc-classifier] section
------------------------

.. _noc-launcher-conf-noc-classifier-enabled:

enabled
^^^^^^^
true/false. Launch noc-classifier daemon

.. _noc-launcher-conf-noc-classifier-user:

user
^^^^
Run noc-classifier daemon with *user* credentials

.. _noc-launcher-conf-noc-classifier-group:

group
^^^^^
Run noc-classifier daemon with *group* credentials

.. _noc-launcher-conf-noc-correlator:

[noc-correlator] section
------------------------

.. _noc-launcher-conf-noc-correlator-enabled:

enabled
^^^^^^^
true/false. Launch noc-correlator daemon

.. _noc-launcher-conf-noc-correlator-user:

user
^^^^
Run noc-correlator daemon with *user* credentials

.. _noc-launcher-conf-noc-correlator-group:

group
^^^^^
Run noc-correlator daemon with *group* credentials

.. _noc-launcher-conf-noc-probe:

[noc-probe] section
-------------------

.. _noc-launcher-conf-noc-probe-enabled:

enabled
^^^^^^^
true/false. Launch noc-probe daemon

.. _noc-launcher-conf-noc-probe-user:

user
^^^^
Run noc-probe daemon with *user* credentials

.. _noc-launcher-conf-noc-probe-group:

group
^^^^^
Run noc-probe daemon with *group* credentials

.. _noc-fcgi-conf:

noc-fcgi.conf
=============
Stores noc-fcgi daemon configuration

.. _noc-fcgi-conf-main:

[main] section
--------------

.. _noc-fcgi-conf-main-logfile:
 
logfile
^^^^^^^
Log file path

.. _noc-fcgi-conf-main-loglevel:

loglevel
^^^^^^^^
logging level. One of: debug, info, warning, error, critical

.. _noc-fcgi-conf-main-logsize:

logsize
^^^^^^^
Maximum log file size in bytes. 0 (default) means unlimited size

.. _noc-fcgi-conf-main-logfiles:

logfiles
^^^^^^^^
Keep *logfiles* backup copies of log file

.. _noc-fcgi-conf-main-pidfile:

pidfile
^^^^^^^
Pid file path

.. _noc-fcgi-conf-fcgi:

[fcgi] section
--------------

.. _noc-fcgi-conf-fcgi-socket:

socket
^^^^^^
Path to UNIX socket to communicate with HTTP server

.. _noc-fcgi-conf-fcgi-minspare:

minspare
^^^^^^^^
Minimum spare worker threads

.. _noc-fcgi-conf-fcgi-maxspare:

maxspare
^^^^^^^^
Maximum spare worker threads

.. _noc-fcgi-conf-fcgi-maxrequests:

maxrequests
^^^^^^^^^^^
Maximum requests processed by worker threads

.. _noc-fcgi-conf-fcgi-maxchildren:

maxchildren
^^^^^^^^^^^
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
^^^^^^^
Log file path

.. _noc-sae-conf-main-loglevel:

loglevel
^^^^^^^^
logging level. One of: debug, info, warning, error, critical

.. _noc-sae-conf-main-logsize:

logsize
^^^^^^^
Maximum log file size in bytes. 0 (default) means unlimited size

.. _noc-sae-conf-main-logfiles:

logfiles
^^^^^^^^
Keep *logfiles* backup copies of log file

.. _noc-sae-conf-main-pidfile:

pidfile
^^^^^^^
Pid file path

.. _noc-sae-conf-sae:

[sae] section
-------------

.. _noc-sae-conf-sae-listen:

listen
^^^^^^
Listen for activator connections at address

.. _noc-sae-conf-sae-port:

port
^^^^
Listen for activator connections at port

.. _noc-sae-conf-sae-refresh_event_filter:

refresh_event_filter
^^^^^^^^^^^^^^^^^^^^
Event filter expire time. Activators will refresh their event filters after this time

.. _noc-sae-conf-sae-ssl_cert:

ssl_cert
^^^^^^^^
Path to the SAE SSL certificate. Certificate must contain public and private parts

.. _noc-sae-conf-sae-ssl_listen:

ssl_listen
^^^^^^^^^^
Listen for activator SSL connections at address

.. _noc-sae-conf-sae-ssl_port:

ssl_port
^^^^^^^^
Listen for activator SSL connections at port

.. _noc-sae-conf-xmlrpc:

xmlrpc section
--------------
SAE XML-RPC server settings.

.. _noc-sae-conf-xmlrpc-listen:

listen
^^^^^^
IP address to listen to XML-RPC connects

.. _noc-sae-conf-xmlrpc-port:

port
^^^^
Port to listen to XML-RPC requests

.. _noc-activator-conf:

noc-activator.conf
==================

Activator configuration

.. _noc-activator-conf-main:

[main] section
--------------

.. _noc-activator-conf-main-logfile:

logfile
^^^^^^^
Log file path

.. _noc-activator-conf-main-loglevel:

loglevel
^^^^^^^^
logging level. One of: debug, info, warning, error, critical

.. _noc-activator-conf-main-logsize:

logsize
^^^^^^^
Maximum log file size in bytes. 0 (default) means unlimited size

.. _noc-activator-conf-main-logfiles:

logfiles
^^^^^^^^
Keep *logfiles* backup copies of log file

.. _noc-activator-conf-main-pidfile:

pidfile
^^^^^^^
Pid file path

.. _noc-activator-conf-activator:

[activator] section
-------------------

.. _noc-activator-conf-activator-name:

name
^^^^
Activator name used for authentication

.. _noc-activator-conf-activator-listen_traps:

listen_traps
^^^^^^^^^^^^
A list of addresses/ports to listen for SNMP Traps. List elements are separated by commas.
Following element formats are acceptable:

* ip
* ip:port
* interface
* interface:port

.. _noc-activator-conf-activator-listen_syslog:

listen_syslog
^^^^^^^^^^^^^
A list of addresses/ports to listen for Syslog. List elements are separated by commas.
Following element formats are acceptable:

* ip
* ip:port
* interface
* interface:port

.. _noc-activator-conf-activator-secret:

secret
^^^^^^
Secret key used for digest authentication

.. _noc-activator-conf-activator-software_update:

software_update
^^^^^^^^^^^^^^^
* true - enable software update on connect.
* false - do not update software on connect

.. _noc-activator-conf-activator-max_pull_config:

max_pull_config
^^^^^^^^^^^^^^^
Maximum concurrent telnet/ssh sessions

.. _noc-activator-conf-sae:

[sae] section
-------------

.. _noc-activator-conf-sae-host:

host
^^^^
Address to be used to connect SAE unless *ssl_host* is not defined

.. _noc-activator-conf-sae-port:

port
^^^^
SAE port

.. _noc-activator-conf-sae-local_address:

local_address
^^^^^^^^^^^^^
Use specified address as source address for SAE connections. Leave empty to use default address.

.. _noc-activator-conf-sae-ssl_host:

ssl_host
^^^^^^^^
Address to be used to connect SAE via SSL, when defined.

.. _noc-activator-conf-sae-ssl_port:

ssl_port
^^^^^^^^
SAE SSL port

.. _noc-activator-conf-path:

[path] section
--------------
Paths to various utilities. This paths are belongs to host on which activator started.

.. _noc-activator-conf-path-fping:

fping
^^^^^
Path to the *fping* utility. *fping* used to perform host reachability detection during ping_check.
*fping* binary must be eighter suid root, or operation system's security options
must be altered to allow generate and receive ICMP packets by *noc* user.

.. _noc-classifier-conf:

noc-classifier.conf
===================
Classifier configuration

.. _noc-classifier-conf-main:

[main] section
--------------

.. _noc-classifier-conf-main-logfile:

logfile
^^^^^^^
Log file path

.. _noc-classifier-conf-main-loglevel:

loglevel
^^^^^^^^
logging level. One of: debug, info, warning, error, critical

.. _noc-classifier-conf-main-logsize:

logsize
^^^^^^^
Maximum log file size in bytes. 0 (default) means unlimited size

.. _noc-classifier-conf-main-logfiles:

logfiles
^^^^^^^^
Keep *logfiles* backup copies of log file

.. _noc-classifier-conf-main-pidfile:

pidfile
^^^^^^^
Pid file path

.. _noc-correlator-conf:

noc-correlator.conf
===================
Correlator configuration

.. _noc-correlator-conf-main:

[main] section
--------------

.. _noc-correlator-conf-main-logfile:

logfile
^^^^^^^
Log file path

.. _noc-correlator-conf-main-loglevel:

loglevel
^^^^^^^^
logging level. One of: debug, info, warning, error, critical

.. _noc-correlator-conf-main-logsize:

logsize
^^^^^^^
Maximum log file size in bytes. 0 (default) means unlimited size

.. _noc-correlator-conf-main-logfiles:

logfiles
^^^^^^^^
Keep *logfiles* backup copies of log file

.. _noc-correlator-conf-main-pidfile:

pidfile
^^^^^^^
Pid file path

.. _noc-correlator-conf-correlator:

[correlator] section
--------------------

.. _noc-correlator-conf-correlator-window:

window
^^^^^^
Window (in seconds) to search active events for correlation process

.. _noc-notifier-conf:

noc-notifier.conf
=================

.. _noc-notifier-conf-main:

[main] section
--------------

.. _noc-notifier-conf-main-logfile:

logfile
^^^^^^^
Log file path

.. _noc-notifier-conf-main-loglevel:

loglevel
^^^^^^^^
logging level. One of: debug, info, warning, error, critical

.. _noc-notifier-conf-main-logsize:

logsize
^^^^^^^
Maximum log file size in bytes. 0 (default) means unlimited size

.. _noc-notifier-conf-main-logfiles:

logfiles
^^^^^^^^
Keep *logfiles* backup copies of log file

.. _noc-notifier-conf-main-pidfile:

pidfile
^^^^^^^
Pid file path

.. _noc-notifier-conf-notifier:

[notifier section]

.. _noc-notifier-conf-notifier-queue_check_interval:

queue_check_interval
^^^^^^^^^^^^^^^^^^^^

Timeout (in seconds) to wait before spooling new bunch of tasks.

.. _noc-notifier-conf-mail:

[mail]

.. _noc-notifier-conf-mail-enabled:

enabled
^^^^^^^

Enable/disable mail delivery (Boolean)

.. _noc-notifier-conf-mail-queue_size:

queue_size
^^^^^^^^^^
SMTP Task queue size. Mail plugin can deliver up to *queue_size* messages in *queue_check_interval* seconds.

.. _noc-notifier-conf-mail-time_to_live:

time_to_live
^^^^^^^^^^^^
Message lifetime. Scheduled message remains actual up to *time_to_live* seconds. If message cannot be delivered
in *time_to_live* seconds it is silently dropped as non-actual.

.. _noc-notifier-conf-mail-retry_interval:

retry_interval
^^^^^^^^^^^^^^
Timeout in seconds to wait after failed message delivery.

.. _noc-notifier-conf-mail-smtp_server:

smtp_server
^^^^^^^^^^^
IP address or FQDN used to connect to the SMTP server

.. _noc-notifier-conf-mail-smtp_port:

smtp_port
^^^^^^^^^
Port used to connect to the SMTP server

.. _noc-notifier-conf-mail-use_tls:

use_tls
^^^^^^^
Enable/Disable SMTP TLS extensions

.. _noc-notifier-conf-mail-smtp_user:

smtp_user
^^^^^^^^^
If defined, perform SMTP server login as *smtp_user* with *smtp_password*

.. _noc-notifier-conf-mail-smtp_password:

smtp_password
^^^^^^^^^^^^^
If defined, perform SMTP server login as *smtp_user* with *smtp_password*

.. _noc-notifier-conf-mail-from_address:

from_address
^^^^^^^^^^^^
Messages From: field

.. _noc-notifier-conf-mail-helo_hostname:

helo_hostname
^^^^^^^^^^^^^
Custom HELO greeting

.. _noc-notifier-conf-file:

[file]

.. _noc-notifier-conf-file-enabled:

enabled
^^^^^^^

Enable/disable file logging (Boolean)

.. _noc-notifier-conf-file-queue_size:

queue_size
^^^^^^^^^^
SMTP Task queue size. File plugin can write up to *queue_size* messages in *queue_check_interval* seconds.

.. _noc-notifier-conf-file-time_to_live:

time_to_live
^^^^^^^^^^^^
Message lifetime. Scheduled message remains actual up to *time_to_live* seconds. If message cannot be written
in *time_to_live* seconds it is silently dropped as non-actual.

.. _noc-notifier-conf-file-retry_interval:

retry_interval
^^^^^^^^^^^^^^
Timeout in seconds to wait after failed message saving attempt.

.. _noc-notifier-conf-file-prefix:

prefix
^^^^^^
A root directory in which all files to be stored. File plugin ignores attempt to save file outside of *prefix* directory.
Full file path is combined from *prefix* and a notification param (relative path)
