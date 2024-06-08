# uptime collector

`uptime` collects system uptime.

## Configuration

| Parameter  | Type             | Default       | Description                                                                                 |
| ---------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`       | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`     | String           |               | Must be `uptime`                                                                            |
| `service`  | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval` | Integer          |               | Repetition interval in seconds                                                              |
| `labels`   | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |

## Collected Metrics

| Metric      | Metric Type | Platform | Description               |
| ----------- | ----------- | -------- | ------------------------- |
| `ts`        |             | All      | ISO 8601 Timestamp        |
| `collector` |             | All      | Collector Id              |
| `labels`    |             | All      | List of labels            |
|             |             |          |                           |
| `uptime`    |             | All      | System uptime, in seconds |

## Compilation Features

Enable `uptime` feature during compiling the agent (Enabled by default).
