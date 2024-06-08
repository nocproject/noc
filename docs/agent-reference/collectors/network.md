# network collector

`network` collects network input/output statistics.

## Configuration

| Parameter  | Type             | Default       | Description                                                                                 |
| ---------- | ---------------- | ------------- | ------------------------------------------------------------------------------------------- |
| `id`       | String           |               | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`     | String           |               | Must be `network`                                                                           |
| `service`  | String           | Equal to `id` | Service id for output metrics                                                               |
| `interval` | Integer          |               | Repetition interval in seconds                                                              |
| `labels`   | Array of Strings |               | List of additional labels. Will be returned along with metrics                              |

## Collected Metrics

| Metric       | Metric Type | Platform | Description        |
| ------------ | ----------- | -------- | ------------------ |
| `ts`         |             | All      | ISO 8601 Timestamp |
| `collector`  |             | All      | Collector Id       |
| `labels`     |             | All      | List of labels     |
|              |             |          |                    |
| `rx_bytes`   |             | All      |                    |
| `tx_bytes`   |             | All      |                    |
| `rx_packets` |             | All      |                    |
| `tx_packets` |             | All      |                    |
| `rx_errors`  |             | All      |                    |
| `tx_errors`  |             | All      |                    |

`network` collector appends following labels

| Label                    | Description            |
| ------------------------ | ---------------------- |
| `noc::interface::{name}` | Network interface name |

## Compilation Features

Enable `network` feature during compiling the agent (Enabled by default).
