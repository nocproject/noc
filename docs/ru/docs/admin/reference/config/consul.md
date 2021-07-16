# [consul] section

Consul service configuration

## token

|                |                    |
| -------------- | ------------------ |
| Default value  | `None`             |
| YAML Path      | `consul.token`     |
| Key-Value Path | `consul/token`     |
| Environment    | `NOC_CONSUL_TOKEN` |

## connect_timeout

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `5s`                         |
| YAML Path      | `consul.connect_timeout`     |
| Key-Value Path | `consul/connect_timeout`     |
| Environment    | `NOC_CONSUL_CONNECT_TIMEOUT` |

## request_timeout

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `1h`                         |
| YAML Path      | `consul.request_timeout`     |
| Key-Value Path | `consul/request_timeout`     |
| Environment    | `NOC_CONSUL_REQUEST_TIMEOUT` |

## near_retry_timeout

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `1`                             |
| YAML Path      | `consul.near_retry_timeout`     |
| Key-Value Path | `consul/near_retry_timeout`     |
| Environment    | `NOC_CONSUL_NEAR_RETRY_TIMEOUT` |

## host

|                |                   |
| -------------- | ----------------- |
| Default value  | `consul`          |
| YAML Path      | `consul.host`     |
| Key-Value Path | `consul/host`     |
| Environment    | `NOC_CONSUL_HOST` |

## port

|                |                   |
| -------------- | ----------------- |
| Default value  | `8500`            |
| YAML Path      | `consul.port`     |
| Key-Value Path | `consul/port`     |
| Environment    | `NOC_CONSUL_PORT` |

## check_interval

|                |                             |
| -------------- | --------------------------- |
| Default value  | `10s`                       |
| YAML Path      | `consul.check_interval`     |
| Key-Value Path | `consul/check_interval`     |
| Environment    | `NOC_CONSUL_CHECK_INTERVAL` |

## check_timeout

|                |                            |
| -------------- | -------------------------- |
| Default value  | `1s`                       |
| YAML Path      | `consul.check_timeout`     |
| Key-Value Path | `consul/check_timeout`     |
| Environment    | `NOC_CONSUL_CHECK_TIMEOUT` |

## release

|                |                      |
| -------------- | -------------------- |
| Default value  | `1M`                 |
| YAML Path      | `consul.release`     |
| Key-Value Path | `consul/release`     |
| Environment    | `NOC_CONSUL_RELEASE` |

## session_ttl

|                |                          |
| -------------- | ------------------------ |
| Default value  | `10s`                    |
| YAML Path      | `consul.session_ttl`     |
| Key-Value Path | `consul/session_ttl`     |
| Environment    | `NOC_CONSUL_SESSION_TTL` |

## lock_delay

|                |                         |
| -------------- | ----------------------- |
| Default value  | `20s`                   |
| YAML Path      | `consul.lock_delay`     |
| Key-Value Path | `consul/lock_delay`     |
| Environment    | `NOC_CONSUL_LOCK_DELAY` |

## retry_timeout

|                |                            |
| -------------- | -------------------------- |
| Default value  | `1s`                       |
| YAML Path      | `consul.retry_timeout`     |
| Key-Value Path | `consul/retry_timeout`     |
| Environment    | `NOC_CONSUL_RETRY_TIMEOUT` |

## keepalive_attempts

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `5`                             |
| YAML Path      | `consul.keepalive_attempts`     |
| Key-Value Path | `consul/keepalive_attempts`     |
| Environment    | `NOC_CONSUL_KEEPALIVE_ATTEMPTS` |

## base

kv lookup base

|                |                   |
| -------------- | ----------------- |
| Default value  | `noc`             |
| YAML Path      | `consul.base`     |
| Key-Value Path | `consul/base`     |
| Environment    | `NOC_CONSUL_BASE` |
