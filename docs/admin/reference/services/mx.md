# mx service

`mx` service accepts the messages addressed to
outside the system, performs routing basing on message headers, and,
possibly, passing it to one of the `sender` services. `mx` is the part
of Generic Message Exchange (GMX) system.

## Service Properties

Sharded
: {{ yes }}

Pooled
: {{ no }}

Databases
: Mongo, Postgres

## Processed Streams

```mermaid
graph LR
   System((System)) -->|mx| mx
   mx -->|kafkasender| kafkasender([kafkasender])
```

### Input Streams

| Stream                                     | Description       |
| ------------------------------------------ | ----------------- |
| [mx](../../../dev/reference/streams/mx.md) | Incoming messages |

### Output Streams

| Stream                                                       | Description                                 |
| ------------------------------------------------------------ | ------------------------------------------- |
| [kafkasender](../../../dev/reference/streams/kafkasender.md) | Messages addressed to outside Kafka cluster |

## Configuration

`mx` service requires no additional configuration.
