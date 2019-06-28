.. _config-memcached:

memcached
---------


.. _config-memcached-addresses:

addresses
~~~~~~~~~

==================  ==================================================================
**YAML Path**       memcached.addresses
**Key-Value Path**  memcached/addresses
**Environment**     NOC_MEMCACHED_ADDRESSES
**Default Value**   ServiceParameter(service='memcached', wait=True, full_result=True)
==================  ==================================================================


.. _config-memcached-pool_size:

pool_size
~~~~~~~~~

==================  =======================
**YAML Path**       memcached.pool_size
**Key-Value Path**  memcached/pool_size
**Environment**     NOC_MEMCACHED_POOL_SIZE
**Default Value**   8
==================  =======================


.. _config-memcached-default_ttl:

default_ttl
~~~~~~~~~~~

==================  =========================
**YAML Path**       memcached.default_ttl
**Key-Value Path**  memcached/default_ttl
**Environment**     NOC_MEMCACHED_DEFAULT_TTL
**Default Value**   1d
==================  =========================


