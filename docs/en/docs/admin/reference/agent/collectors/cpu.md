# cpu collector

`cpu` collects CPU usage statistics.

## Configuration

| Parameter  | Type             | Default       | Description                                                                                 |
| ---------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`       | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`     | String           |               | Must be `cpu`                                                                               |
| `service`  | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval` | Integer          |               | Repetition interval in seconds                                                              |
| `labels`   | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |

## Collected Metrics

| Metric      | Metric Type | Platform | Description        |
| ----------- | ----------- | -------- | ------------------ |
| `ts`        |             | All      | ISO 8601 Timestamp |
| `collector` |             | All      | Collector Id       |
| `labels`    |             | All      | List of labels     |
|             |             |          |                    |
| `user`      |             | All      |                    |
| `nice`      |             | All      |                    |
| `system`    |             | All      |                    |
| `interrupt` |             | All      |                    |
| `idle`      |             | All      |                    |
|             |             |          |                    |
| `iowait`    |             | Linux    |                    |

`cpu` collector appends following labels

| Label              | Description |
| ------------------ | ----------- |
| `noc::cpu::{name}` | CPU number  |

## Compilation Features

Enable `cpu` feature during compiling the agent (Enabled by default).
