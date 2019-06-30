.. _config-redis:

redis
-----


.. _config-redis-addresses:

addresses
~~~~~~~~~

==================  ==============================================================
**YAML Path**       redis.addresses
**Key-Value Path**  redis/addresses
**Environment**     NOC_REDIS_ADDRESSES
**Default Value**   ServiceParameter(service="redis", wait=True, full_result=True)
==================  ==============================================================


.. _config-redis-db:

db
~~

==================  ============
**YAML Path**       redis.db
**Key-Value Path**  redis/db
**Environment**     NOC_REDIS_DB
**Default Value**   0
==================  ============


.. _config-redis-default_ttl:

default_ttl
~~~~~~~~~~~

==================  =====================
**YAML Path**       redis.default_ttl
**Key-Value Path**  redis/default_ttl
**Environment**     NOC_REDIS_DEFAULT_TTL
**Default Value**   1d
==================  =====================


