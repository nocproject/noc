# metricscollector service

`metricscollector` services receives telemetry data from `noc-agent`,
normalizes and checks them and spools the result to the [metrics](metrics.md)
service.

## Service Properties

Sharded
: {{ yes }}

Pooled
: {{ no }}

Databases
: mongo

## Processed streams

```mermaid
graph LR
   metricscollector([metricscollector]) -->|metrics| metrics
```

### Output Streams

| Stream                                     | Description               |
| ------------------------------------------ | ------------------------- |
| [metrics](../streams-reference/metrics.md) | Normalized telemetry data |

## Configuration

`metricscollector` service may be configured via [[metricscollector]](../config-reference/metricscollector.md)
config section.
