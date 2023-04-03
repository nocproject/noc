# [ping] section

[Ping](../services/ping.md) service configuration

## throttle_threshold

|                |                               |
| -------------- | ----------------------------- |
| Default value  | `None`                        |
| YAML Path      | `ping.throttle_threshold`     |
| Key-Value Path | `ping/throttle_threshold`     |
| Environment    | `NOC_PING_THROTTLE_THRESHOLD` |

## restore_threshold

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `None`                       |
| YAML Path      | `ping.restore_threshold`     |
| Key-Value Path | `ping/restore_threshold`     |
| Environment    | `NOC_PING_RESTORE_THRESHOLD` |

## tos

Default value
: 0

Possible values
: 0..255

YAML Path
: ping.tos

Key-Value Path
: ping/tos

Environment
: NOC_PING_TOS

## send_buffer

|                |                        |
| -------------- | ---------------------- |
| Default value  | `4 * 1048576`          |
| YAML Path      | `ping.send_buffer`     |
| Key-Value Path | `ping/send_buffer`     |
| Environment    | `NOC_PING_SEND_BUFFER` |

## receive_buffer

|                |                           |
| -------------- | ------------------------- |
| Default value  | `4 * 1048576`             |
| YAML Path      | `ping.receive_buffer`     |
| Key-Value Path | `ping/receive_buffer`     |
| Environment    | `NOC_PING_RECEIVE_BUFFER` |

## ds_limit

|                |                     |
| -------------- | ------------------- |
| Default value  | `1000`              |
| YAML Path      | `ping.ds_limit`     |
| Key-Value Path | `ping/ds_limit`     |
| Environment    | `NOC_PING_DS_LIMIT` |
