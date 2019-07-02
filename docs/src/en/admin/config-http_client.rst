.. _config-http_client:

http_client
-----------


.. _config-http_client-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ===============================
**YAML Path**       http_client.connect_timeout
**Key-Value Path**  http_client/connect_timeout
**Environment**     NOC_HTTP_CLIENT_CONNECT_TIMEOUT
**Default Value**   10s
==================  ===============================


.. _config-http_client-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ===============================
**YAML Path**       http_client.request_timeout
**Key-Value Path**  http_client/request_timeout
**Environment**     NOC_HTTP_CLIENT_REQUEST_TIMEOUT
**Default Value**   1h
==================  ===============================


.. _config-http_client-user_agent:

user_agent
~~~~~~~~~~

==================  ==========================
**YAML Path**       http_client.user_agent
**Key-Value Path**  http_client/user_agent
**Environment**     NOC_HTTP_CLIENT_USER_AGENT
**Default Value**   noc
==================  ==========================


.. _config-http_client-buffer_size:

buffer_size
~~~~~~~~~~~

==================  ===========================
**YAML Path**       http_client.buffer_size
**Key-Value Path**  http_client/buffer_size
**Environment**     NOC_HTTP_CLIENT_BUFFER_SIZE
**Default Value**   128 * 1024
==================  ===========================


.. _config-http_client-max_redirects:

max_redirects
~~~~~~~~~~~~~

==================  =============================
**YAML Path**       http_client.max_redirects
**Key-Value Path**  http_client/max_redirects
**Environment**     NOC_HTTP_CLIENT_MAX_REDIRECTS
**Default Value**   5
==================  =============================


.. _config-http_client-ns_cache_size:

ns_cache_size
~~~~~~~~~~~~~

==================  =============================
**YAML Path**       http_client.ns_cache_size
**Key-Value Path**  http_client/ns_cache_size
**Environment**     NOC_HTTP_CLIENT_NS_CACHE_SIZE
**Default Value**   1000
==================  =============================


.. _config-http_client-resolver_ttl:

resolver_ttl
~~~~~~~~~~~~

==================  ============================
**YAML Path**       http_client.resolver_ttl
**Key-Value Path**  http_client/resolver_ttl
**Environment**     NOC_HTTP_CLIENT_RESOLVER_TTL
**Default Value**   3s
==================  ============================


.. _config-http_client-http_port:

http_port
~~~~~~~~~

==================  =========================
**YAML Path**       http_client.http_port
**Key-Value Path**  http_client/http_port
**Environment**     NOC_HTTP_CLIENT_HTTP_PORT
**Default Value**   80
==================  =========================


.. _config-http_client-https_port:

https_port
~~~~~~~~~~

==================  ==========================
**YAML Path**       http_client.https_port
**Key-Value Path**  http_client/https_port
**Environment**     NOC_HTTP_CLIENT_HTTPS_PORT
**Default Value**   443
==================  ==========================


.. _config-http_client-validate_certs:

validate_certs
~~~~~~~~~~~~~~

Have to be set as True

==================  ==============================
**YAML Path**       http_client.validate_certs
**Key-Value Path**  http_client/validate_certs
**Environment**     NOC_HTTP_CLIENT_VALIDATE_CERTS
**Default Value**   False
==================  ==============================


