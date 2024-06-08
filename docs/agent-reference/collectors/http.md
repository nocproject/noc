# http collector

`http` collector performs HTTP request and collects the response performance data.

## Configuration

| Parameter  | Type             | Default       | Description                                                                                 |
| ---------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`       | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`     | String           |               | Must be `http`                                                                              |
| `service`  | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval` | Integer          |               | Repetition interval in seconds                                                              |
| `labels`   | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |
| `url`      | String           |               | Request url                                                                                 |

## Collected Metrics

| Metric             | Metric Type | Platform                   | Description                  |
| ------------------ | ----------- | -------------------------- | ---------------------------- |
| `ts`               |             | All                        | ISO 8601 Timestamp           |
| `collector`        |             | All                        | Collector Id                 |
| `labels`           |             | All                        | List of labels               |
|                    |             |                            |                              |
| `time`             |             | All                        | Response time                |
| `bytes`            |             | All                        | Response size (uncompressed) |
| `compressed_bytes` |             | Response size (compressed) |                              |

## Compilation Features

Enable `http` feature during compiling the agent (Enabled by default).
