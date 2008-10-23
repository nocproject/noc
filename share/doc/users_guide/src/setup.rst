#####
Setup
#####

----------------
site-settings.py
----------------
You should set up site-settings.py file before
starting any NOC proccesses. The best way to
populate site-settings.py is to make copy from sample file

::

    cd <nocroot>
    cp site-settings.py.sample site-settings.py
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

site-settings.py is a python script which evaluated at the start of the NOC processes.
site-settings.py contains database password and secret key and should be kept
with strict permissions.

You should set up several variables.

DEBUG
-----
Should web interface report exceptions to user's browser or exception should be send to
the ADMINS members.

||True||Report exception to the user||
||False||Report exception to ADMINS||

ADMINS
-------

A list of pairs (Name,Email) to notify about exceptions when DEBUG variable is False

Example:

::

    ADMINS = (
        ("admin1","admin1@example.com"),
        ("admin2","admin2@example.com"),
    )

DATABASE_ENGINE
---------------
Database engine for NOC. Should be set to "postgresql_psycopg2"

Example:

::

    DATABASE_ENGINE = "postgresql_psycopg2"

DATABASE_NAME
-------------
The name of database.

Example:

::

    DATABASE_NAME = "noc"

DATABASE_USER
-------------
Username for database connection. Should be valid postgresql user.
Please refer to postgresql documentation (http://www.postgresql.org/docs/8.3/interactive/database-roles.html)

Exapmle:

::

    DATABASE_USER = "noc"

DATABASE_PASSWORD
-----------------
Password for database connection.

Example:

::

    DATABASE_PASSWORD = "nocpass"

DATABASE_HOST
-------------
IP or FQDN of Postresql server or empty string to use UNIX sockets.

Example:

::

    DATABASE_HOST = ""

DATABASE_PORT
-------------
Port for database connection or empty string when using UNIX sockets

Example:

::

    DATABASE_PORT = ""

TIME_ZONE
---------
Local time zone for this installation.
Choices can be found here:
http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
although not all variations may be possible on all operating systems.
If running in a Windows environment this must be set to the same as your
system time zone.

Example:

::

    TIME_ZONE = "Europe/Moscow"

LANGUAGE_CODE
-------------
Language code for this installation. All choices can be found here:
http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
Only en-us supported for this moment.

Example:

::

    LANGUAGE_CODE = 'en-us'

SECRET_KEY
----------
Random string to secure session data. Make this key unique and don't share
with anybody.

Example:

::

    SECRET_KEY = 'j82icp#5zBUZ!4hx^#0s4)dy8sru@1ynqblq2!1lv1lu=7&(58'

---------------------------
Web interface. Setup module
---------------------------

cm.vcs_path
-----------

cm.vcs_type
-----------

dns.rsync_target
----------------

dns.zone_cache
--------------

tt.url
------

shell.rsync
-----------

shell.ssh
---------