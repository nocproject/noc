---
date: 2023-10-11
authors: [dv]
description: >
    How to host mkdocs-generated site properly
categories:
    - Tech
---
# Hosting an Mkdocs-generated Site Using Nginx

Creating exceptional software documentation is a pivotal ingredient for product success. The NOC Team has been on a relentless journey with "Project Aegeus" to make our documentation truly shine. While top-notch content is essential, the delivery process plays a crucial role in shaping the user experience. In this post, we're shifting our focus to delivery, where we'll reveal some tricks that can take your documentation from good to great.

Mkdocs, especially when adorned with the stylish mkdocs-material theme, is an outstanding tool for crafting project documentation. The outcome is a directory brimming with polished HTML files and a treasure trove of static assets. Unlike popular CMS platforms like Joomla or WordPress, your output is a self-contained directory that doesn't rely on additional runtime services or databases. This independence makes it incredibly easy to serve your documentation directly to your audience. While services like "GitHub Pages" and "Read the Docs" have their allure, there's a compelling case for hosting your documentation independently. We, for instance, rely on the rock-solid Nginx web server. In the following sections, we'll offer you a glimpse into our setup and share some simple yet highly effective tweaks to enhance performance.
<!-- more -->

Let's take a glance at our setup. Here and after we consider that `<site>` should
be replaced with your domain name. We also consider you have nginx installed and running.

## Checking mkdocs.yml

Check `mkdocs.yml` file and ensure, your `site_url` setting is valid:

``` yaml
site_url: https://<site>/
```

!!! warning

    `https://` prefix is viable for our setup.

## DNS Setup

Add `A` record to your DNS Zone to reach your site

``` txt
@   IN  A  <ip>
```

Where `<ip>` is an IP address of your nginx server.

## Nginx Configuration

Let's take a closer look at our configuration. We are creating two virtual servers, one for HTTP on port 80, and the other for HTTPS on port 443. Each virtual server has its own configuration
file. I.e. `<site>:80.conf` and `<site>:443.conf`, though you can use eevery other names to your pleasure.

## HTTP Setup

Create a first configuration file, named `<site>:80.conf`, replacing `<site>` with your domain name.

``` txt title="site:80.conf" linenums="1"
--8<-- "docs/blog/posts/serving-mkdocs-site/http.conf"
```

And place it into one of the following paths, depending on your system:

* `/etc/nginx/conf.d/<site>.conf`
* `/etc/nginx/sites-available/<site>.conf`

If you choose to place config in `sites-available` directory, do not
forget to create a symlink to enable config:

``` shell
# cd /etc/nginx/sites-enabled/
# ln -s /etc/nginx/sites-available/<site>:80.conf .
```

Then check configuration:

``` shell
# nginx -T
...
# echo $?
0
```

If you did all correctly, the command will complete wihout errors and you will
see `0` as result of the `echo`.

Reload configuration:

``` shell
# service nginx reload
```

Let's examine the configuration:

``` txt title="site:80.conf" linenums="1" hl_lines="2 3"
--8<-- "docs/blog/posts/serving-mkdocs-site/http.conf"
```

Listen for virtual site `<site>` on default HTTP port 80.

``` txt title="site:80.conf" linenums="1" hl_lines="5 6"
--8<-- "docs/blog/posts/serving-mkdocs-site/http.conf"
```

Set up logging.

``` txt title="site:80.conf" linenums="1" hl_lines="8 9 10 11"
--8<-- "docs/blog/posts/serving-mkdocs-site/http.conf"
```

We using Certbot to obtain TLS certificates from Letsencrypt.
We're creating a well-known entrypoint to process an
certificate request. We'll explain Certbot setup in separate
blog post.

``` txt title="site:80.conf" linenums="1" hl_lines="13 14 15"
--8<-- "docs/blog/posts/serving-mkdocs-site/http.conf"
```

We forcing our users to use HTTPS, redirecting all other requests
to the HTTPS version of the site.

## Certbot Setup

Prior to passing to HTTPS section we need to receive TLS certificate.
We're using Certbot to requiest certificates via Letsencrypt.

To request the certificate:

```
# certbot --nginx -d <site>
```

Check for our certificates are present in place:

```
# ls /etc/letsencrypt/live/<site>/
fullchain.pem
privkey.pem
```

## HTTPS Setup

If all is correct, create file named `<site>:443.conf`, replacing `<site>` with your domain name.

``` txt title="site:443.conf" linenums="1"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf"
```

And place it into one of the following paths, depending on your system:

* `/etc/nginx/conf.d/<site>.conf`
* `/etc/nginx/sites-available/<site>.conf`

If you choose to place config in `sites-available` directory, do not
forget to create a symlink to enable config:

``` shell
# cd /etc/nginx/sites-enabled/
# ln -s /etc/nginx/sites-available/<site>:443.conf .
```

Then check configuration:

``` shell
# nginx -T
...
# echo $?
0
```

If you did all correctly, the command will complete wihout errors and you will
see `0` as result of the `echo`.

Reload configuration:

``` shell
# service nginx reload
```

Let's examine the configuration:

``` txt title="site:443.conf" linenums="2" hl_lines="1 2"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:1:14"
```

Listen for virtual site `<site>` on default HTTPЫ port 443
and enable HTTP/2.

``` txt title="site:443.conf" linenums="2" hl_lines="4"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:1:14"
```
Enable TLSv1.3 and TLSv1.2, do not use an older versions.

``` txt title="site:443.conf" linenums="2" hl_lines="5 6"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:1:14"
```
Use TLS certificates, prepared by Certbot.

``` txt title="site:443.conf" linenums="2" hl_lines="7"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:1:14"
```
Always set `Strict-Transport-Security` header to enable HSTS.
The HSTS nforms browsers that the site should only be accessed using HTTPS, and that any future attempts to access it using HTTP should automatically be converted to HTTPS.

``` txt title="site:443.conf" linenums="2" hl_lines="8 9"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:1:14"
```
Enable Online Certificate Status Protocol (OSCP) stapling to check
the revocation status of the certificates in the efficient mannner.

``` txt title="site:443.conf" linenums="2" hl_lines="11 12"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:1:14"
```

Set up logging.

``` txt title="site:443.conf" linenums="15" hl_lines="1"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:15:22"
```
Serve static files from `/www/<site>/` directory. We use minio's
S3 endpoint to deliver our documentation, though you can simple
put your files in place using any available method.

``` txt title="site:443.conf" linenums="15" hl_lines="2"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:15:22"
```

Replace nginx's default 404 page with the fancy page, provided
by mkdocs-material. This is a very important step for a better
user experience, as the customized page provides all standard
navigation and search and allows user to find all needed
information.

``` txt title="site:443.conf" linenums="15" hl_lines="4"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:15:22"
```
Set `X-Content-Type-Options` header for all replices to indicate that the MIME types advertised in the Content-Type headers should be followed and not be changed. The header allows you to avoid MIME type sniffing by saying that the MIME types are deliberately configured.

``` txt title="site:443.conf" linenums="15" hl_lines="6 7"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:15:22"
```
Enable gzip compression for all browsers. The HTML, CSS, JSON, and XML files
will be automatically compressed for all modern browsers. Data compression
is significantly reduces traffic, which gains serious benefits to the
mobile users and increases the page loading speed. We have optimized
compression for mkdocs-material generated content.

``` txt title="site:443.conf" linenums="23" hl_lines="1 2 3 4"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:23"
```

Some files may be served yet more efficently. In this section
we define an additional handling for minified CSS and JS content
of the mkdocs-material theme. mkdocs-material adds an hash
to the file name to increase the caching efficiency.

We set an `Cache-Control`  header to inform the browser to store the minified files for a week
and to do not request them again while user navigating through
our doc.

We also set `Surrogate-Control` header to inform upstream CDNs to cache reply whenever possible.

Proper caching of the files is an another step in enhancing the user experience.

``` txt title="site:443.conf" linenums="23" hl_lines="6 7 8 9"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:23"
```
Mkdocs-material stores a database for online search in the `search_index.json` file.
This JSON file may be really large for the complex documentations. For example,
NOC's one is about 4 megabytes. As we constantly updating our content, we cannot
cache this file for a long time, so one hour is an reasonable default.
We're setting `Cache-Control` and `Surrogate-Control` options in the same
way as for minified files.

``` txt title="site:443.conf" linenums="23" hl_lines="11 12 13"
--8<-- "docs/blog/posts/serving-mkdocs-site/https.conf:23"
```
We're using Minio to upload our content, so we need to protect
minio's internal database from accidental exposure. So we
simple denying access to the internal directory.

## Adding robots.txt

Finally, we would make the life easier for the search engine bots. Just place
`robots.txt` to your `docs/` directory to always generate it with your docs.
Do not forget to replace `<site>` with your domain name.

``` txt title="robots.txt" linenums="1"
--8<-- "docs/blog/posts/serving-mkdocs-site/robots.txt"
```
The content is simple: Allow all to index our docs and notify the bots
that we have fancy sitemap, generated by mkdocs-material.

## Results

We have used a Lighthouse tool, provided with Google Chrome to evaluate
an user experience. We've estimated the performance of our home page:
https://getnoc.com/

Prior the changes, using standard boilerplate for static files, we have
overall performance of 75.

After applying all tweaks we have reached an overall performance of 97.

![Lighthouse screenshot](lighthouse.png)

Proposed methods can be used by everyone, who wish to host mkdocs-material
sites and require only default set of nginx' features. We're hoping
that our esse will help you to increase an user experience of your docs.