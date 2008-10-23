############
Installation
############

-----------
Getting NOC
-----------

NOC is under development stage. Best way to get NOC is to fetch
from mercurial repository.

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
    

Postgresql
==========

http://www.postgresql.org/

PostgreSQL is the world's leading open-source database and the NOC's primary database engine.

Python
======

http://www.python.org/

Python is a universal dynamic object-oriented language. NOC mostly written in python language.

psycopg2
========

http://initd.org/

Psycopg2 is a PosgtreSQL database connector for Python

Django
======

http://www.djangoproject.com/

Django is a high-level Python Web Framework. NOC uses Django for Web interface
and Django's ORM for database access. 

South
=====

http://south.aeracode.org/

South is an intelligent schema migrations tool for Django. South allows seamless
database migrations during software updates.

flup
====
http://trac.saddi.com/flup

Flup is a FastCGI connector for Python

HTTP Server
===========

Any FastCGI-capable server is required for NOC Web-interface.
Possible web servers are
||Apache||http://www.apache.org/||
||Lighttpd||http://www.lighttpd.net/||
We are using lighttpd for production use.

Mercurial
=========

http://www.selenic.com/mercurial/

Mercurial is dictributed version control system widely used in NOC's
development process.

Sphinx
======

http://sphinx.pocoo.org/

Sphinx is a python documentation generator. All NOC documentation
is a sphinx sources. You need sphinx to rebuild HTML and printable
documentation.

--------------
Database Setup
--------------
::

    createuser noc
    createdb -EUTF8 noc
    cd <nocroot>
    python manage.py syncdb
    python manage.py migrate
    
-----------------
HTTP Server setup
-----------------

Apache
======

Lighttpd
========

::

    server.modules              = (
                                "mod_rewrite",
                                "mod_redirect",
                                "mod_alias",
                                "mod_access",
                                "mod_accesslog" )
    fastcgi.server = (
        "/noc.fcgi" => (
                "main" => (
                        "socket"      => "/tmp/nocd.fcgi",
                        "check-local" => "disable",
                         )
        )
    )
    
    $HTTP["host"] == "noc.effortel.ru" {
        server.document-root        = "/var/www/noc"
        alias.url=(
            "/media/"  => "/opt/csw/lib/python/site-packages/django/contrib/admin/media/",
            "/static/" => "/var/www/noc/static/",
        )
        url.rewrite-once=(
            "^(/media.*)$" => "$1",
            "^/static/(.*)$"  => "/static/$1",
            "^(/.*)$" => "/noc.fcgi$1",
        )
        accesslog.filename="/var/log/lighttpd/noc.effortel.ru.access.log"
    }
    
    $SERVER["socket"] == ":443" {
        ssl.engine = "enable"
        ssl.pemfile ="/opt/csw/etc/lighttpd.pem"
    }


----------
Solaris 10
----------
All NOC daemons can be run via Solaris SMF

::

    svccfg import /var/www/noc/share/smf/sae.xml
    svccfg -s application/sae setprop sae/pidfile=/var/log/noc/sae.pid
    svccfg -s application/sae setprop sae/logfile=/var/log/noc/sae.log
    svccfg -s application/sae:default refresh
