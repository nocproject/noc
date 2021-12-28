# [web] section

[Web](../services/web.md) service configuration

## theme

|                |                 |
| -------------- | --------------- |
| Default value  | `gray`          |
| YAML Path      | `web.theme`     |
| Key-Value Path | `web/theme`     |
| Environment    | `NOC_WEB_THEME` |

## api_row_limit

|                |                         |
| -------------- | ----------------------- |
| Default value  | `0`                     |
| YAML Path      | `web.api_row_limit`     |
| Key-Value Path | `web/api_row_limit`     |
| Environment    | `NOC_WEB_API_ROW_LIMIT` |

## api_unlimited_row_limit

|                |                                   |
| -------------- | --------------------------------- |
| Default value  | `1000`                            |
| YAML Path      | `web.api_unlimited_row_limit`     |
| Key-Value Path | `web/api_unlimited_row_limit`     |
| Environment    | `NOC_WEB_API_UNLIMITED_ROW_LIMIT` |

## api_arch_alarm_limit

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `4 * 86400`                    |
| YAML Path      | `web.api_arch_alarm_limit`     |
| Key-Value Path | `web/api_arch_alarm_limit`     |
| Environment    | `NOC_WEB_API_ARCH_ALARM_LIMIT` |

## max_upload_size

The maximum size in bytes that a request body may be
before a RequestDataTooBig is raised.

|                |                           |
| -------------- | ------------------------- |
| Default value  | `16777216`                |
| YAML Path      | `web.max_upload_size`     |
| Key-Value Path | `web/max_upload_size`     |
| Environment    | `NOC_WEB_MAX_UPLOAD_SIZE` |

## language

|                |                    |
| -------------- | ------------------ |
| Default value  | `en`               |
| YAML Path      | `web.language`     |
| Key-Value Path | `web/language`     |
| Environment    | `NOC_WEB_LANGUAGE` |

## install_collection

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `False`                      |
| YAML Path      | `web.install_collection`     |
| Key-Value Path | `web/install_collection`     |
| Environment    | `NOC_WEB_INSTALL_COLLECTION` |

## max_threads

|                |                       |
| -------------- | --------------------- |
| Default value  | `10`                  |
| YAML Path      | `web.max_threads`     |
| Key-Value Path | `web/max_threads`     |
| Environment    | `NOC_WEB_MAX_THREADS` |

## macdb_window

|                |                        |
| -------------- | ---------------------- |
| Default value  | `4 * 86400`            |
| YAML Path      | `web.macdb_window`     |
| Key-Value Path | `web/macdb_window`     |
| Environment    | `NOC_WEB_MACDB_WINDOW` |

## enable_remote_system_last_extract_info

|                |                                                  |
| -------------- | ------------------------------------------------ |
| Default value  | `False`                                          |
| YAML Path      | `web.enable_remote_system_last_extract_info`     |
| Key-Value Path | `web/enable_remote_system_last_extract_info`     |
| Environment    | `NOC_WEB_ENABLE_REMOTE_SYSTEM_LAST_EXTRACT_INFO` |
