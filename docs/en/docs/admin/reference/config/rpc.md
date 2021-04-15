# [rpc] section

Rpc service configuration

## retry_timeout

|                |                         |
| -------------- | ----------------------- |
| Default value  | `0.1,0.5,1,3,10,30`     |
| YAML Path      | `rpc.retry_timeout`     |
| Key-Value Path | `rpc/retry_timeout`     |
| Environment    | `NOC_RPC_RETRY_TIMEOUT` |

## sync_connect_timeout

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `20s`                          |
| YAML Path      | `rpc.sync_connect_timeout`     |
| Key-Value Path | `rpc/sync_connect_timeout`     |
| Environment    | `NOC_RPC_SYNC_CONNECT_TIMEOUT` |

## sync_request_timeout

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `1h`                           |
| YAML Path      | `rpc.sync_request_timeout`     |
| Key-Value Path | `rpc/sync_request_timeout`     |
| Environment    | `NOC_RPC_SYNC_REQUEST_TIMEOUT` |

## sync_retry_timeout

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `1.0`                        |
| YAML Path      | `rpc.sync_retry_timeout`     |
| Key-Value Path | `rpc/sync_retry_timeout`     |
| Environment    | `NOC_RPC_SYNC_RETRY_TIMEOUT` |

## sync_retry_delta

|                |                            |
| -------------- | -------------------------- |
| Default value  | `2.0`                      |
| YAML Path      | `rpc.sync_retry_delta`     |
| Key-Value Path | `rpc/sync_retry_delta`     |
| Environment    | `NOC_RPC_SYNC_RETRY_DELTA` |

## sync_retries

|                |                        |
| -------------- | ---------------------- |
| Default value  | `5`                    |
| YAML Path      | `rpc.sync_retries`     |
| Key-Value Path | `rpc/sync_retries`     |
| Environment    | `NOC_RPC_SYNC_RETRIES` |

## async_connect_timeout

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `20s`                           |
| YAML Path      | `rpc.async_connect_timeout`     |
| Key-Value Path | `rpc/async_connect_timeout`     |
| Environment    | `NOC_RPC_ASYNC_CONNECT_TIMEOUT` |

## async_request_timeout

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `1h`                            |
| YAML Path      | `rpc.async_request_timeout`     |
| Key-Value Path | `rpc/async_request_timeout`     |
| Environment    | `NOC_RPC_ASYNC_REQUEST_TIMEOUT` |
