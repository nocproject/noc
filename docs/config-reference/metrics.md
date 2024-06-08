# [metrics] section

[metrics](../services-reference/metrics.md) service configuration

## compact_on_start

Run log compaction on service start

|                 |                                |
| --------------- | ------------------------------ |
| Default value   | `True`                         |
| Possible values | `True` or `False`              |
| YAML Path       | `metrics.compact_on_start`     |
| Key-Value Path  | `metrics/compact_on_start`     |
| Environment     | `NOC_METRICS_COMPACT_ON_START` |

## compact_on_stop

Run log compaction on service stop

|                 |                               |
| --------------- | ----------------------------- |
| Default value   | `True`                        |
| Possible values | `True` or `False`             |
| YAML Path       | `metrics.compact_on_stop`     |
| Key-Value Path  | `metrics/compact_on_stop`     |
| Environment     | `NOC_METRICS_COMPACT_ON_STOP` |

## flush_interval

Flushing is the process on moving collected changes from memory to persistent storage.
You may loose up to `flush_interval` seconds of changes on unexpected crash.

To disable runtime flushing set parameter to `0`. Changes will be flushed on
graceful shutdown anyway.

|                 |                              |
| --------------- | ---------------------------- |
| Default value   | `1s`                         |
| Possible values |                              |
| YAML Path       | `metrics.flush_interval`     |
| Key-Value Path  | `metrics/flush_interval`     |
| Environment     | `NOC_METRICS_FLUSH_INTERVAL` |

## compact_interval

Compacting is the process on aggregating the incremental changes to a larger chunks.
Compacting allows to reduce disk space used by change log.

To disable runtime compacting set parameter to `0`. Compacting still may be performed
on service startup or shutdown when setting `compact_on_start` or `compact_on_stop`
parameters.

!!! warning

    Disabling of runtime compaction may lead to unlimited disk usages and may
    greatly increase the service startup time.

|                 |                              |
| --------------- | ---------------------------- |
| Default value   | `1s`                         |
| Possible values |                              |
| YAML Path       | `metrics.flush_interval`     |
| Key-Value Path  | `metrics/flush_interval`     |
| Environment     | `NOC_METRICS_FLUSH_INTERVAL` |



