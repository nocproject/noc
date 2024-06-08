# [memcached] section

Memcached service configuration

## addresses

|                |                                                    |
| -------------- | -------------------------------------------------- |
| Default value  | `service="memcached", wait=True, full_result=True` |
| YAML Path      | `memcached.addresses`                              |
| Key-Value Path | `memcached/addresses`                              |
| Environment    | `NOC_MEMCACHED_ADDRESSES`                          |

## pool_size

|                |                           |
| -------------- | ------------------------- |
| Default value  | `8`                       |
| YAML Path      | `memcached.pool_size`     |
| Key-Value Path | `memcached/pool_size`     |
| Environment    | `NOC_MEMCACHED_POOL_SIZE` |

## default_ttl

|                |                             |
| -------------- | --------------------------- |
| Default value  | `1d`                        |
| YAML Path      | `memcached.default_ttl`     |
| Key-Value Path | `memcached/default_ttl`     |
| Environment    | `NOC_MEMCACHED_DEFAULT_TTL` |
