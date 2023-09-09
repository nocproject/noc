# [trapcollector] section

[Trapcollector](../services/trapcollector.md) service configuration

## listen

|                |                            |
| -------------- | -------------------------- |
| Default value  | `0.0.0.0:162`              |
| YAML Path      | `trapcollector.listen`     |
| Key-Value Path | `trapcollector/listen`     |
| Environment    | `NOC_TRAPCOLLECTOR_LISTEN` |

## enable_reuseport

|                |                                      |
| -------------- | ------------------------------------ |
| Default value  | `True`                               |
| YAML Path      | `trapcollector.enable_reuseport`     |
| Key-Value Path | `trapcollector/enable_reuseport`     |
| Environment    | `NOC_TRAPCOLLECTOR_ENABLE_REUSEPORT` |

## enable_freebind

|                |                                     |
| -------------- | ----------------------------------- |
| Default value  | `False`                             |
| YAML Path      | `trapcollector.enable_freebind`     |
| Key-Value Path | `trapcollector/enable_freebind`     |
| Environment    | `NOC_TRAPCOLLECTOR_ENABLE_FREEBIND` |

## ds_limit

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `1000`                       |
| YAML Path      | `trapcollector.ds_limit`     |
| Key-Value Path | `trapcollector/ds_limit`     |
| Environment    | `NOC_TRAPCOLLECTOR_DS_LIMIT` |
