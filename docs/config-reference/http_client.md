# [http_client] section

Http_client service configuration

## connect_timeout

|                |                                   |
| -------------- | --------------------------------- |
| Default value  | `10s`                             |
| YAML Path      | `http_client.connect_timeout`     |
| Key-Value Path | `http_client/connect_timeout`     |
| Environment    | `NOC_HTTP_CLIENT_CONNECT_TIMEOUT` |

## request_timeout

|                |                                   |
| -------------- | --------------------------------- |
| Default value  | `1h`                              |
| YAML Path      | `http_client.request_timeout`     |
| Key-Value Path | `http_client/request_timeout`     |
| Environment    | `NOC_HTTP_CLIENT_REQUEST_TIMEOUT` |

## user_agent

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `noc`                        |
| YAML Path      | `http_client.user_agent`     |
| Key-Value Path | `http_client/user_agent`     |
| Environment    | `NOC_HTTP_CLIENT_USER_AGENT` |

## buffer_size

|                |                               |
| -------------- | ----------------------------- |
| Default value  | `131072`                      |
| YAML Path      | `http_client.buffer_size`     |
| Key-Value Path | `http_client/buffer_size`     |
| Environment    | `NOC_HTTP_CLIENT_BUFFER_SIZE` |

## max_redirects

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `5`                             |
| YAML Path      | `http_client.max_redirects`     |
| Key-Value Path | `http_client/max_redirects`     |
| Environment    | `NOC_HTTP_CLIENT_MAX_REDIRECTS` |

## ns_cache_size

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `1000`                          |
| YAML Path      | `http_client.ns_cache_size`     |
| Key-Value Path | `http_client/ns_cache_size`     |
| Environment    | `NOC_HTTP_CLIENT_NS_CACHE_SIZE` |

## resolver_ttl

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `3s`                           |
| YAML Path      | `http_client.resolver_ttl`     |
| Key-Value Path | `http_client/resolver_ttl`     |
| Environment    | `NOC_HTTP_CLIENT_RESOLVER_TTL` |

## http_port

|                |                             |
| -------------- | --------------------------- |
| Default value  | `80`                        |
| YAML Path      | `http_client.http_port`     |
| Key-Value Path | `http_client/http_port`     |
| Environment    | `NOC_HTTP_CLIENT_HTTP_PORT` |

## https_port

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `443`                        |
| YAML Path      | `http_client.https_port`     |
| Key-Value Path | `http_client/https_port`     |
| Environment    | `NOC_HTTP_CLIENT_HTTPS_PORT` |

## validate_certs

Have to be set as True

|                |                                  |
| -------------- | -------------------------------- |
| Default value  | `False`                          |
| YAML Path      | `http_client.validate_certs`     |
| Key-Value Path | `http_client/validate_certs`     |
| Environment    | `NOC_HTTP_CLIENT_VALIDATE_CERTS` |
