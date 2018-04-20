.. _webserver:

Setting Up Webserver
********************

Common Considerations
=====================
Common practice is to set up HTTP-server as frontend serving static files and
proxy all dynamic requests to the ``noc-web`` daemon. Static content URLs:

* ``/media/`` must be mapped to ``/opt/noc/contrib/lib/django/contrib/admin/media/`` directory
* ``/static/`` must be mapped to ``/opt/noc/static/``

Lighttpd Setup
==============

Set up lighttpd.conf::

    server.modules              = (
                                "mod_rewrite",
                                "mod_redirect",
                                "mod_alias",
                                "mod_access",
                                "mod_proxy",
                                "mod_accesslog" )
    
    static-file.etags = "enable"
    etag.use-mtime = "enable"
    
    proxy.server = (
        "/noc.proxy" => (("host" => "127.0.0.1", "port" => 8000))
        )
    )
    
    $HTTP["host"] == "yourdomain" {
        server.document-root        = "/opt/noc"
        alias.url=(
            "/media/"  => "/opt/noc/contrib/lib/django/contrib/admin/media/",
            "/static/" => "/opt/noc/static/",
        )
        url.rewrite-once=(
            "^(/media.*)$" => "$1",
            "^/static/(.*)$"  => "/static/$1",
            "^(/.*)$" => "/noc.proxy$1",
        )
        accesslog.filename="/var/log/lighttpd/yourdomain.access.log"
    }

Nginx setup
===========
Set up nginx.conf::

    worker_processes  1;
    events {
        worker_connections  1024;
    }
    http {
        include       mime.types;
        default_type  application/octet-stream;
        sendfile        on;
        keepalive_timeout  15;
        server {
            listen       80;
            server_name  yourdomain;
            location /media/ {
                alias /opt/noc/contrib/lib/django/contrib/admin/media/;
                gzip on;
                gzip_types text/css text/x-js;
            }
            location /static/ {
                alias /opt/noc/static/;
                gzip on;
                gzip_types text/css text/x-js;
            }
            location / {
                proxy_pass http://127.0.0.1:8000/;
            }
        }
    }

Apache Setup
============
Set up httpd.conf::

    FastCGIExternalServer /opt/noc/noc.fcgi -socket /tmp/noc.fcgi
    
    <VirtualHost *:80>
        DocumentRoot    /opt/noc
        ServerName      yourdomain
        Alias  /media /opt/noc/contrib/lib/django/contrib/admin/media/
        RewriteEngine On
        RewriteRule ^/(media.*)$ /$1 [QSA,L,PT]
        RewriteRule ^/(static.*)$  /$1 [QSA,L,PT]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteRule ^/(.*)$ /noc.fcgi/$1 [QSA,L]
        <Directory /opt/noc>
            Order allow,deny
            Allow from all
        </Directory>
        <Location /media>
            Order allow,deny
            Allow from all
        </Location>
    </VirtualHost>

