============
Installation
============

-----------
Getting NOC
-----------

------------
Supported OS
------------

NOC was created to work at almost any UNIX-style systems.
NOC is reported to run successfully at:

* MacOS X
* Solaris 10

    
-----------------
Required Packages
-----------------

The following packages are required for NOC
    

##########
Postgresql
##########

http://www.postgresql.org/

PostgreSQL is the world's leading open-source database and the NOC's primary database engine.

######
Python
######

http://www.python.org/

Python is a universal dynamic object-oriented language. NOC mostly written in python language.

########
psycopg2
########

######
Django
######

#####
South
#####

###########
HTTP Server
###########

#########
Mercurial
#########

######
Sphinx
######


--------------
Database Setup
--------------
::

    createuser noc
    createdb -EUTF8 noc
    python manage.py syncdb
    python manage.py migrate

----------
Solaris 10
----------
::

    svccfg import /var/www/noc/share/smf/sae.xml
    svccfg -s application/sae setprop sae/pidfile=/var/log/noc/sae.pid
    svccfg -s application/sae setprop sae/logfile=/var/log/noc/sae.log
    svccfg -s application/sae:default refresh
