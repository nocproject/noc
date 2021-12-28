# [bi] section

[Bi](../services/bi.md) service configuration

## language

Language BI interface

|                |                   |
| -------------- | ----------------- |
| Default value  | `en`              |
| YAML Path      | `bi.language`     |
| Key-Value Path | `bi/language`     |
| Environment    | `NOC_BI_LANGUAGE` |

## query_threads

|                |                        |
| -------------- | ---------------------- |
| Default value  | `10`                   |
| YAML Path      | `bi.query_threads`     |
| Key-Value Path | `bi/query_threads`     |
| Environment    | `NOC_BI_QUERY_THREADS` |

## extract_delay_alarms

|                |                               |
| -------------- | ----------------------------- |
| Default value  | `1h`                          |
| YAML Path      | `bi.extract_delay_alarms`     |
| Key-Value Path | `bi/extract_delay_alarms`     |
| Environment    | `NOC_BI_EXTRACT_DELAY_ALARMS` |

## clean_delay_alarms

|                |                             |
| -------------- | --------------------------- |
| Default value  | `1d`                        |
| YAML Path      | `bi.clean_delay_alarms`     |
| Key-Value Path | `bi/clean_delay_alarms`     |
| Environment    | `NOC_BI_CLEAN_DELAY_ALARMS` |

## reboot_interval

|                |                          |
| -------------- | ------------------------ |
| Default value  | `1M`                     |
| YAML Path      | `bi.reboot_interval`     |
| Key-Value Path | `bi/reboot_interval`     |
| Environment    | `NOC_BI_REBOOT_INTERVAL` |

## extract_delay_reboots

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `1h`                           |
| YAML Path      | `bi.extract_delay_reboots`     |
| Key-Value Path | `bi/extract_delay_reboots`     |
| Environment    | `NOC_BI_EXTRACT_DELAY_REBOOTS` |

## clean_delay_reboots

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `1d`                         |
| YAML Path      | `bi.clean_delay_reboots`     |
| Key-Value Path | `bi/clean_delay_reboots`     |
| Environment    | `NOC_BI_CLEAN_DELAY_REBOOTS` |

## chunk_size

|                |                     |
| -------------- | ------------------- |
| Default value  | `500`               |
| YAML Path      | `bi.chunk_size`     |
| Key-Value Path | `bi/chunk_size`     |
| Environment    | `NOC_BI_CHUNK_SIZE` |

## extract_window

|                |                         |
| -------------- | ----------------------- |
| Default value  | `1d`                    |
| YAML Path      | `bi.extract_window`     |
| Key-Value Path | `bi/extract_window`     |
| Environment    | `NOC_BI_EXTRACT_WINDOW` |

## enable_alarms

|                |                        |
| -------------- | ---------------------- |
| Default value  | `False`                |
| YAML Path      | `bi.enable_alarms`     |
| Key-Value Path | `bi/enable_alarms`     |
| Environment    | `NOC_BI_ENABLE_ALARMS` |

## enable_reboots

|                |                         |
| -------------- | ----------------------- |
| Default value  | `False`                 |
| YAML Path      | `bi.enable_reboots`     |
| Key-Value Path | `bi/enable_reboots`     |
| Environment    | `NOC_BI_ENABLE_REBOOTS` |

## enable_managedobjects

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `False`                        |
| YAML Path      | `bi.enable_managedobjects`     |
| Key-Value Path | `bi/enable_managedobjects`     |
| Environment    | `NOC_BI_ENABLE_MANAGEDOBJECTS` |

## enable_alarms_archive

|                |                                |
| -------------- | ------------------------------ |
| Default value  | `False`                        |
| YAML Path      | `bi.enable_alarms_archive`     |
| Key-Value Path | `bi/enable_alarms_archive`     |
| Environment    | `NOC_BI_ENABLE_ALARMS_ARCHIVE` |

## alarms_archive_policy

Default value
: weekly

Possible values
:

- weekly
- monthly
- quarterly
- yearly

YAML Path
: bi.alarms_archive_policy

Key-Value Path
: bi/alarms_archive_policy

Environment
: NOC_BI_ALARMS_ARCHIVE_POLICY

## alarms_archive_batch_limit

|                |                                     |
| -------------- | ----------------------------------- |
| Default value  | `10000`                             |
| YAML Path      | `bi.alarms_archive_batch_limit`     |
| Key-Value Path | `bi/alarms_archive_batch_limit`     |
| Environment    | `NOC_BI_ALARMS_ARCHIVE_BATCH_LIMIT` |
