# twamp_reflector collector

`twamp_reflector` is the reflector part of TWAMP protocol. Though not producing
metrics directly, `twamp_reflector` responds to [`twamp_sender`](twamp_sender.md)
probes.

## Configuration

| Parameter  | Type             | Default | Description                                                                                 |
| ---------- | ---------------- | ------- | ------------------------------------------------------------------------------------------- |
| `id`       | String           |         | Collector's ID. Must be unique per agent instance. Will be returned along with the metrics. |
| `type`     | String           |         | Must be `twamp_reflector`                                                                   |
| `interval` | Integer          |         | Repetition interval in seconds                                                              |
| `labels`   | Array of Strings |         | List of additional labels. Will be returned along with metrics                              |
|            |                  |         |                                                                                             |
| `listen`   | String           |         |                                                                                             |
| `port`     | Integer          | `862`   |                                                                                             |

## Compilation Features

Enable `twamp-reflector` feature during compiling the agent (Enabled by default).
