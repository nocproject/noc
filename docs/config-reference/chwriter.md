# [chwriter] section

[chwriter](../services-reference/chwriter.md) service configuration

## shard_id

Shard identifier served by [chwriter](../services-reference/chwriter.md) instance.
Use default value for unsharded configurations.

|                |                         |
| -------------- | ----------------------- |
| Default value  | `0`                     |
| YAML Path      | `chwriter.shard_id`     |
| Key-Value Path | `chwriter/shard_id`     |
| Environment    | `NOC_CHWRITER_SHARD_ID` |

## replica_id

Shard's replica identifier served by [chwriter](../services-reference/chwriter.md) instance.
Use default value for unreplicated configurations.

|                |                           |
| -------------- | ------------------------- |
| Default value  | `0`                       |
| YAML Path      | `chwriter.replica_id`     |
| Key-Value Path | `chwriter/replica_id`     |
| Environment    | `NOC_CHWRITER_REPLICA_ID` |

## batch_size

Desired size of the write batch, in records

|                |                           |
| -------------- | ------------------------- |
| Default value  | `50000`                   |
| YAML Path      | `chwriter.batch_size`     |
| Key-Value Path | `chwriter/batch_size`     |
| Environment    | `NOC_CHWRITER_BATCH_SIZE` |

## batch_delay_ms

Send every period time

|                |                               |
| -------------- | ----------------------------- |
| Default value  | `10000`                       |
| YAML Path      | `chwriter.batch_delay_ms`     |
| Key-Value Path | `chwriter/batch_delay_ms`     |
| Environment    | `NOC_CHWRITER_BATCH_DELAY_MS` |

## write_to

|                |                         |
| -------------- | ----------------------- |
| Default value  |                         |
| YAML Path      | `chwriter.write_to`     |
| Key-Value Path | `chwriter/write_to`     |
| Environment    | `NOC_CHWRITER_WRITE_TO` |
