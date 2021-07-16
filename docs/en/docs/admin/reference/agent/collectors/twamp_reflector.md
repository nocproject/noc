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

## Configuring senders

### noc-agent

```yaml
collectors:
  - id: TWAMP G.711 Test
    type: twamp_sender
    interval: 10
    server: 10.0.0.1
    port: 862
    dscp: ef
    n_packets: 250
    model: g711
    test_timeout: 3
```

For details on packet models and configuration and parameters refer to
the [twamp_sender](twamp_sender.md) documentation.
