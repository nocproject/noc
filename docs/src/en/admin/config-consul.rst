.. _config-consul:

consul
------


.. _config-consul-token:

token
~~~~~

==================  =================
**YAML Path**       consul.token
**Key-Value Path**  consul/token
**Environment**     NOC_CONSUL_TOKEN
**Default Value**   SecretParameter()
==================  =================


.. _config-consul-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       consul.connect_timeout
**Key-Value Path**  consul/connect_timeout
**Environment**     NOC_CONSUL_CONNECT_TIMEOUT
**Default Value**   5s
==================  ==========================


.. _config-consul-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       consul.request_timeout
**Key-Value Path**  consul/request_timeout
**Environment**     NOC_CONSUL_REQUEST_TIMEOUT
**Default Value**   1h
==================  ==========================


.. _config-consul-near_retry_timeout:

near_retry_timeout
~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       consul.near_retry_timeout
**Key-Value Path**  consul/near_retry_timeout
**Environment**     NOC_CONSUL_NEAR_RETRY_TIMEOUT
**Default Value**   1
==================  =============================


.. _config-consul-host:

host
~~~~

==================  ===============
**YAML Path**       consul.host
**Key-Value Path**  consul/host
**Environment**     NOC_CONSUL_HOST
**Default Value**   consul
==================  ===============


.. _config-consul-port:

port
~~~~

==================  ===============
**YAML Path**       consul.port
**Key-Value Path**  consul/port
**Environment**     NOC_CONSUL_PORT
**Default Value**   8500
==================  ===============


.. _config-consul-check_interval:

check_interval
~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       consul.check_interval
**Key-Value Path**  consul/check_interval
**Environment**     NOC_CONSUL_CHECK_INTERVAL
**Default Value**   10s
==================  =========================


.. _config-consul-check_timeout:

check_timeout
~~~~~~~~~~~~~

==================  ========================
**YAML Path**       consul.check_timeout
**Key-Value Path**  consul/check_timeout
**Environment**     NOC_CONSUL_CHECK_TIMEOUT
**Default Value**   1s
==================  ========================


.. _config-consul-release:

release
~~~~~~~

==================  ==================
**YAML Path**       consul.release
**Key-Value Path**  consul/release
**Environment**     NOC_CONSUL_RELEASE
**Default Value**   1M
==================  ==================


.. _config-consul-session_ttl:

session_ttl
~~~~~~~~~~~

==================  ======================
**YAML Path**       consul.session_ttl
**Key-Value Path**  consul/session_ttl
**Environment**     NOC_CONSUL_SESSION_TTL
**Default Value**   10s
==================  ======================


.. _config-consul-lock_delay:

lock_delay
~~~~~~~~~~

==================  =====================
**YAML Path**       consul.lock_delay
**Key-Value Path**  consul/lock_delay
**Environment**     NOC_CONSUL_LOCK_DELAY
**Default Value**   20s
==================  =====================


.. _config-consul-retry_timeout:

retry_timeout
~~~~~~~~~~~~~

==================  ========================
**YAML Path**       consul.retry_timeout
**Key-Value Path**  consul/retry_timeout
**Environment**     NOC_CONSUL_RETRY_TIMEOUT
**Default Value**   1s
==================  ========================


.. _config-consul-keepalive_attempts:

keepalive_attempts
~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       consul.keepalive_attempts
**Key-Value Path**  consul/keepalive_attempts
**Environment**     NOC_CONSUL_KEEPALIVE_ATTEMPTS
**Default Value**   5
==================  =============================


.. _config-consul-base:

base
~~~~

kv lookup base

==================  ===============
**YAML Path**       consul.base
**Key-Value Path**  consul/base
**Environment**     NOC_CONSUL_BASE
**Default Value**   noc
==================  ===============


