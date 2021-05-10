# block_io collector

`block_io` collects block-devices input/output statistics.

## Configuration

| Parameter  | Type             | Default       | Description                                                                                 |
| ---------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`       | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`     | String           |               | Must be `block_io`                                                                          |
| `service`  | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval` | Integer          |               | Repetition interval in seconds                                                              |
| `labels`   | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |

## Collected Metrics

| Metric          | Metric Type | Platform | Description        |
| --------------- | ----------- | -------- | ------------------ |
| `ts`            |             | All      | ISO 8601 Timestamp |
| `collector`     |             | All      | Collector Id       |
| `labels`        |             | All      | List of labels     |
|                 |             |          |                    |
| `read_ios`      |             | All      |                    |
| `read_merges`   |             | All      |                    |
| `read_sectors`  |             | All      |                    |
| `read_ticks`    |             | All      |                    |
| `write_ios`     |             | All      |                    |
| `write_merges`  |             | All      |                    |
| `write_sectors` |             | All      |                    |
| `write_ticks`   |             | All      |                    |
| `in_flight`     |             | All      |                    |
| `io_ticks`      |             | All      |                    |
| `time_in_queue` |             | All      |                    |

`block_io` collector appends following labels

| Label              | Description       |
| ------------------ | ----------------- |
| `noc::dev::{name}` | Block device name |

## Compilation Features

Enable `block-io` feature during compiling the agent (Enabled by default).
