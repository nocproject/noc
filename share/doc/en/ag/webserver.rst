********************
Setting Up Webserver
********************

Common Considerations
=====================
Common practice is to set up HTTP-server as frontend serving static files and
routing all dynamic requests to the ``noc-fcgi`` daemon over FastCGI. Static content URLs:

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
            "/media/"  => "/opt/noc/contrib/lib/django/contrib/admin/media/",
            "/static/" => "/opt/noc/static/",
        )
        url.rewrite-once=(
            "^(/media.*)$" => "$1",
            "^/static/(.*)$"  => "/static/$1",
            "^(/.*)$" => "/noc.fcgi$1",
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
        keepalive_timeout  65;
        server {
            listen       80;
            server_name  <yourdomain>;
            error_page   500 502 503 504  /50x.html;
            location = /50x.html {
                root   /usr/local/www/nginx-dist;
            }
              location / {
                root   html;
                index  index.html index.htm;
                fastcgi_pass unix:/tmp/noc.fcgi;
                fastcgi_param  SERVER_PROTOCOL    $server_protocol;
                fastcgi_param  SERVER_PORT        $server_port;
                fastcgi_param  SERVER_NAME        $server_name;
                fastcgi_param PATH_INFO $fastcgi_script_name;
                fastcgi_param REQUEST_METHOD $request_method;
                fastcgi_param QUERY_STRING $query_string;
                fastcgi_param CONTENT_TYPE $content_type;
                fastcgi_param CONTENT_LENGTH $content_length;
                fastcgi_pass_header Authorization;
                fastcgi_intercept_errors off;
             }
            location /media {
                root /opt/noc/contrib/lib/django/contrib/admin/;
                }
            location /static {
                root /opt/noc/;
                }
            rewrite ^/static/(.*)$ /static/$1 last;
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
        RewriteRule ^/(.*)$ /mysite.fcgi/$1 [QSA,L]    
        <Directory /opt/noc>
            Order allow,deny
            Allow from all
        </Directory>
        <Location /media>
            Order allow,deny
            Allow from all
        </Location>
    </VirtualHost>

