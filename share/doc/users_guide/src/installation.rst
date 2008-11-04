############
Installation
############

------------
Supported OS
------------

NOC was created to work at almost any UNIX-style systems.
NOC is reported to run successfully at:

* MacOS X
* Solaris 10

-----------------
Required Software
-----------------
NOC Requires Python 2.5 or later and PostgreSQL 8.0 or later in order to
run installation script. The rest of software will be downloaded and
installed automatically. Production use also requires HTTP server with
FastCGI support (Lighttpd, Apache+mod_fastcgi)

-----------
Getting NOC
-----------

NOC is under development stage. Best way to get NOC is to fetch
from mercurial repository.

::

    mkdir /var/www/noc
    cd /var/www
    hg clone ssh://hg@hg.effortel.ru/noc noc

------------
Installation
------------

::

    cd noc
    python setup.py install


    
-----------------------------------------------
Required Software (Left until setup.py working)
-----------------------------------------------

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
                        "socket"      => "/tmp/noc.fcgi",
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

--------------
Database Setup
--------------
::

    createuser noc
    createdb -EUTF8 noc
    cd /var/www/noc
    python manage.py syncdb
    python manage.py migrate
    
----------------
Solaris 10 Notes
----------------
All NOC daemons can be managed via Solaris SMF.
share/sunos/manifest directory contains SMF Manifests.
Manifests are imported automatically during installation process.


::

    svccfg import /var/www/noc/share/sunos/manifests/noc-sae.xml
    svccfg -s application/noc-sae setprop sae/pidfile=/var/log/noc/noc-sae.pid
    svccfg -s application/noc-sae setprop sae/logfile=/var/log/noc/noc-sae.log
    svccfg -s application/noc-sae:default refresh
