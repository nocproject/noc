# [syslogcollector] section

[Syslogcollector](../services-reference/syslogcollector.md) service configuration

## listen

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `0.0.0.0:514`                |
| YAML Path      | `syslogcollector.listen`     |
| Key-Value Path | `syslogcollector/listen`     |
| Environment    | `NOC_SYSLOGCOLLECTOR_LISTEN` |

## enable_reuseport

|                |                                        |
| -------------- | -------------------------------------- |
| Default value  | `True`                                 |
| YAML Path      | `syslogcollector.enable_reuseport`     |
| Key-Value Path | `syslogcollector/enable_reuseport`     |
| Environment    | `NOC_SYSLOGCOLLECTOR_ENABLE_REUSEPORT` |

## enable_freebind

|                |                                       |
| -------------- | ------------------------------------- |
| Default value  | `False`                               |
| YAML Path      | `syslogcollector.enable_freebind`     |
| Key-Value Path | `syslogcollector/enable_freebind`     |
| Environment    | `NOC_SYSLOGCOLLECTOR_ENABLE_FREEBIND` |

## ds_limit

DataStream request limit

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `1000`                         |
| YAML Path      | `syslogcollector.ds_limit`     |
| Key-Value Path | `syslogcollector/ds_limit`     |
| Environment    | `NOC_SYSLOGCOLLECTOR_DS_LIMIT` |
