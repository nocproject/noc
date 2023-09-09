# [activator] section

[Activator](../services/activator.md) service configuration

## tos

Set [Type of Service](https://en.wikipedia.org/wiki/Type_of_service) for
all outgoing CLI/SNMP requests.

|                 |                     |
| --------------- | ------------------- |
| Default value   | `0`                 |
| Possible values | `0`..`255`          |
| YAML Path       | `activator.tos`     |
| Key-Value Path  | `activator/tos`     |
| Environment     | `NOC_ACTIVATOR_TOS` |

## script_threads

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `10`                           |
| YAML Path      | `activator.script_threads`     |
| Key-Value Path | `activator/script_threads`     |
| Environment    | `NOC_ACTIVATOR_SCRIPT_THREADS` |

## buffer_size

|                |                             |
| -------------- | --------------------------- |
| Default value  | `1048576`                   |
| YAML Path      | `activator.buffer_size`     |
| Key-Value Path | `activator/buffer_size`     |
| Environment    | `NOC_ACTIVATOR_BUFFER_SIZE` |

## connect_retries

retries on immediate disconnect

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `3`                             |
| YAML Path      | `activator.connect_retries`     |
| Key-Value Path | `activator/connect_retries`     |
| Environment    | `NOC_ACTIVATOR_CONNECT_RETRIES` |

## connect_timeout

timeout after immediate disconnect

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `3`                             |
| YAML Path      | `activator.connect_timeout`     |
| Key-Value Path | `activator/connect_timeout`     |
| Environment    | `NOC_ACTIVATOR_CONNECT_TIMEOUT` |

## http_connect_timeout

|                |                                      |
| -------------- | ------------------------------------ |
| Default value  | `20`                                 |
| YAML Path      | `activator.http_connect_timeout`     |
| Key-Value Path | `activator/http_connect_timeout`     |
| Environment    | `NOC_ACTIVATOR_HTTP_CONNECT_TIMEOUT` |

## http_request_timeout

|                |                                      |
| -------------- | ------------------------------------ |
| Default value  | `30`                                 |
| YAML Path      | `activator.http_request_timeout`     |
| Key-Value Path | `activator/http_request_timeout`     |
| Environment    | `NOC_ACTIVATOR_HTTP_REQUEST_TIMEOUT` |

## http_validate_cert

|                |                                    |
| -------------- | ---------------------------------- |
| Default value  | `False`                            |
| YAML Path      | `activator.http_validate_cert`     |
| Key-Value Path | `activator/http_validate_cert`     |
| Environment    | `NOC_ACTIVATOR_HTTP_VALIDATE_CERT` |
