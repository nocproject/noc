# dns collector

`dns` collects query statistics.

## Configuration

| Parameter     | Type             | Default       | Description                                                                                 |
| ------------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`          | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`        | String           |               | Must be `dns`                                                                               |
| `service`     | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval`    | Integer          |               | Repetition interval in seconds                                                              |
| `labels`      | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |
| `query`       | String           |               |
| `query_type`  | String           | `A`           |
| `n`           | Integer          | `1`           |
| `min_success` | Integer          | `1`           |

## Collected Metrics

| Metric      | Metric Type | Platform | Description        |
| ----------- | ----------- | -------- | ------------------ |
| `ts`        |             | All      | ISO 8601 Timestamp |
| `collector` |             | All      | Collector Id       |
| `labels`    |             | All      | List of labels     |
|             |             |          |                    |
| `total`     |             | All      |                    |
| `success`   |             | All      |                    |
| `failed`    |             | All      |                    |
| `min_ns`    |             | All      |                    |
| `max_ns`    |             | All      |                    |
| `avg_ns`    |             | All      |                    |
| `jitter_ns` |             | All      |                    |

## Compilation Features

Enable `dns` feature during compiling the agent (Enabled by default).
