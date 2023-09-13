# fs collector

`fs` collects file system statistics.

## Configuration

| Parameter  | Type             | Default       | Description                                                                                 |
| ---------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`       | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`     | String           |               | Must be `fs`                                                                                |
| `service`  | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval` | Integer          |               | Repetition interval in seconds                                                              |
| `labels`   | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |

## Collected Metrics

| Metric        | Metric Type | Platform | Description        |
| ------------- | ----------- | -------- | ------------------ |
| `ts`          |             | All      | ISO 8601 Timestamp |
| `collector`   |             | All      | Collector Id       |
| `labels`      |             | All      | List of labels     |
|               |             |          |                    |
| `files`       |             | All      |                    |
| `files_total` |             | All      |                    |
| `files_avail` |             | All      |                    |
| `free`        |             | All      |                    |
| `avail`       |             | All      |                    |
| `total`       |             | All      |                    |

`fs` collector appends following labels

| Label                 | Description     |
| --------------------- | --------------- |
| `noc::fs::{name}`     | Filesystem name |
| `noc::fstype::{name}` | Filesystem type |

## Compilation Features

Enable `fs` feature during compiling the agent (Enabled by default).
