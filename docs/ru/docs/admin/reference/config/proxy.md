# [proxy] section

Proxy service configuration

## http_proxy

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `os.environ.get("http_proxy")` |
| YAML Path      | `proxy.http_proxy`             |
| Key-Value Path | `proxy/http_proxy`             |
| Environment    | `NOC_PROXY_HTTP_PROXY`         |

## https_proxy

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `os.environ.get("http_proxy")` |
| YAML Path      | `proxy.https_proxy`            |
| Key-Value Path | `proxy/https_proxy`            |
| Environment    | `NOC_PROXY_HTTPS_PROXY`        |

## ftp_proxy

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `os.environ.get("http_proxy")` |
| YAML Path      | `proxy.ftp_proxy`              |
| Key-Value Path | `proxy/ftp_proxy`              |
| Environment    | `NOC_PROXY_FTP_PROXY`          |
