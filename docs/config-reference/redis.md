# [redis] section

Redis service configuration

## addresses

|                |                                                |
| -------------- | ---------------------------------------------- |
| Default value  | `service="redis", wait=True, full_result=True` |
| YAML Path      | `redis.addresses`                              |
| Key-Value Path | `redis/addresses`                              |
| Environment    | `NOC_REDIS_ADDRESSES`                          |

## db

|                |                |
| -------------- | -------------- |
| Default value  | `0`            |
| YAML Path      | `redis.db`     |
| Key-Value Path | `redis/db`     |
| Environment    | `NOC_REDIS_DB` |

## default_ttl

|                |                         |
| -------------- | ----------------------- |
| Default value  | `1d`                    |
| YAML Path      | `redis.default_ttl`     |
| Key-Value Path | `redis/default_ttl`     |
| Environment    | `NOC_REDIS_DEFAULT_TTL` |
