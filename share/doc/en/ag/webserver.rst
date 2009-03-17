********************
Setting Up Webserver
********************

Common Considerations
=====================
Common practice is to set up HTTP-server as frontend serving static files and
routing all dynamic requests to the ``noc-fcgi`` daemon over FastCGI. Static content URLs:

* ``/media/`` must be mapped to ``<django-root>/contrib/admin/media/`` directory
* ``/static/`` must be mapped to ``/opt/noc/static/``

Lighttpd Setup
==============

Set up lighttpd.conf::

    server.modules              = (
                                "mod_rewrite",
                                "mod_redirect",
                                "mod_alias",
                                "mod_access",
                                "mod_fastcgi",
                                "mod_accesslog" )
    
    static-file.etags = "enable"
    etag.use-mtime = "enable"
    
    fastcgi.server = (
        "/noc.fcgi" => (
                "main" => (
                        "socket"      => "/tmp/noc.fcgi",
                        "check-local" => "disable",
                         )
        )
    )
    
    $HTTP["host"] == "yourdomain" {
        server.document-root        = "/opt/noc"
        alias.url=(
            "/media/"  => "<django-root>/contrib/admin/media/",
            "/static/" => "/opt/noc/static/",
        )
        url.rewrite-once=(
            "^(/media.*)$" => "$1",
            "^/static/(.*)$"  => "/static/$1",
            "^(/.*)$" => "/noc.fcgi$1",
        )
        accesslog.filename="/var/log/lighttpd/yourdomain.access.log"
    }

Apache Setup
============
