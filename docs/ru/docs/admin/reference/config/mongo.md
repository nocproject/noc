# [mongo] section

Mongo service configuration

## addresses

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `service="mongo", wait=True` |
| YAML Path      | `mongo.addresses`            |
| Key-Value Path | `mongo/addresses`            |
| Environment    | `NOC_MONGO_ADDRESSES`        |

## db

|                |                |
| -------------- | -------------- |
| Default value  | `noc`          |
| YAML Path      | `mongo.db`     |
| Key-Value Path | `mongo/db`     |
| Environment    | `NOC_MONGO_DB` |

## user

|                |                  |
| -------------- | ---------------- |
| Default value  | ``               |
| YAML Path      | `mongo.user`     |
| Key-Value Path | `mongo/user`     |
| Environment    | `NOC_MONGO_USER` |

## password

|                |                      |
| -------------- | -------------------- |
| Default value  | `None`               |
| YAML Path      | `mongo.password`     |
| Key-Value Path | `mongo/password`     |
| Environment    | `NOC_MONGO_PASSWORD` |

## rs

|                |                |
| -------------- | -------------- |
| Default value  | ``             |
| YAML Path      | `mongo.rs`     |
| Key-Value Path | `mongo/rs`     |
| Environment    | `NOC_MONGO_RS` |

## retries

|                |                     |
| -------------- | ------------------- |
| Default value  | `20`                |
| YAML Path      | `mongo.retries`     |
| Key-Value Path | `mongo/retries`     |
| Environment    | `NOC_MONGO_RETRIES` |

## timeout

|                |                     |
| -------------- | ------------------- |
| Default value  | `3s`                |
| YAML Path      | `mongo.timeout`     |
| Key-Value Path | `mongo/timeout`     |
| Environment    | `NOC_MONGO_TIMEOUT` |

## retry_writes

|                |                          |
| -------------- | ------------------------ |
| Default value  | `False`                  |
| YAML Path      | `mongo.retry_writes`     |
| Key-Value Path | `mongo/retry_writes`     |
| Environment    | `NOC_MONGO_RETRY_WRITES` |

## app_name

|                |                      |
| -------------- | -------------------- |
| Default value  | ``                   |
| YAML Path      | `mongo.app_name`     |
| Key-Value Path | `mongo/app_name`     |
| Environment    | `NOC_MONGO_APP_NAME` |

## max_idle_time

|                |                           |
| -------------- | ------------------------- |
| Default value  | `60s`                     |
| YAML Path      | `mongo.max_idle_time`     |
| Key-Value Path | `mongo/max_idle_time`     |
| Environment    | `NOC_MONGO_MAX_IDLE_TIME` |
