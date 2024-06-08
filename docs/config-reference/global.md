# Global service configuration

Global settings applicable to all services

## loglevel

Default value
: info

Possible values
: _ critical
_ error
_ warning
_ info \* debug

YAML Path
: loglevel

Key-Value Path
: loglevel

Environment
: NOC_LOGLEVEL

## brand

|                |             |
| -------------- | ----------- |
| Default value  | `NOC`       |
| YAML Path      | `brand`     |
| Key-Value Path | `brand`     |
| Environment    | `NOC_BRAND` |

## global_n_instances

|                |                          |
| -------------- | ------------------------ |
| Default value  | `1`                      |
| YAML Path      | `global_n_instances`     |
| Key-Value Path | `global_n_instances`     |
| Environment    | `NOC_GLOBAL_N_INSTANCES` |

## installation_name

|                |                             |
| -------------- | --------------------------- |
| Default value  | `Unconfigured installation` |
| YAML Path      | `installation_name`         |
| Key-Value Path | `installation_name`         |
| Environment    | `NOC_INSTALLATION_NAME`     |

## installation_id

|                |                       |
| -------------- | --------------------- |
| Default value  | ``                    |
| YAML Path      | `installation_id`     |
| Key-Value Path | `installation_id`     |
| Environment    | `NOC_INSTALLATION_ID` |

## instance

|                |                |
| -------------- | -------------- |
| Default value  | `0`            |
| YAML Path      | `instance`     |
| Key-Value Path | `instance`     |
| Environment    | `NOC_INSTANCE` |

## language

|                |                |
| -------------- | -------------- |
| Default value  | `en`           |
| YAML Path      | `language`     |
| Key-Value Path | `language`     |
| Environment    | `NOC_LANGUAGE` |

## language_code

|                |                     |
| -------------- | ------------------- |
| Default value  | `en`                |
| YAML Path      | `language_code`     |
| Key-Value Path | `language_code`     |
| Environment    | `NOC_LANGUAGE_CODE` |

## listen

|                |              |
| -------------- | ------------ |
| Default value  | `auto:0`     |
| YAML Path      | `listen`     |
| Key-Value Path | `listen`     |
| Environment    | `NOC_LISTEN` |

## log_format

|                |                                      |
| -------------- | ------------------------------------ |
| Default value  | `%(asctime)s [%(name)s] %(message)s` |
| YAML Path      | `log_format`                         |
| Key-Value Path | `log_format`                         |
| Environment    | `NOC_LOG_FORMAT`                     |

## thread_stack_size

|                |                         |
| -------------- | ----------------------- |
| Default value  | `0`                     |
| YAML Path      | `thread_stack_size`     |
| Key-Value Path | `thread_stack_size`     |
| Environment    | `NOC_THREAD_STACK_SIZE` |

## version_format

|                |                                                   |
| -------------- | ------------------------------------------------- |
| Default value  | `%(version)s+%(branch)s.%(number)s.%(changeset)s` |
| YAML Path      | `version_format`                                  |
| Key-Value Path | `version_format`                                  |
| Environment    | `NOC_VERSION_FORMAT`                              |

## node

|                |                        |
| -------------- | ---------------------- |
| Default value  | `socket.gethostname()` |
| YAML Path      | `node`                 |
| Key-Value Path | `node`                 |
| Environment    | `NOC_NODE`             |

## pool

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `os.environ.get("NOC_POOL", ")` |
| YAML Path      | `pool`                          |
| Key-Value Path | `pool`                          |
| Environment    | `NOC_POOL`                      |

## secret_key

|                |                  |
| -------------- | ---------------- |
| Default value  | `12345`          |
| YAML Path      | `secret_key`     |
| Key-Value Path | `secret_key`     |
| Environment    | `NOC_SECRET_KEY` |

## timezone

|                |                 |
| -------------- | --------------- |
| Default value  | `Europe/Moscow` |
| YAML Path      | `timezone`      |
| Key-Value Path | `timezone`      |
| Environment    | `NOC_TIMEZONE`  |
