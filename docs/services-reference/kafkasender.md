# kafkasender Service

`kafkasender` service receives messages from [mx](mx.md) service
and performs safe delivery to outside Kafka cluster. Messages are
delivered as-is according to `To` header and `Kafka-Partition`
if the parameter is specified.
`kafkasender` is the part
of Generic Message Exchange (GMX) system.

## Service Properties

Sharded
: {{ yes }}

Pooled
: {{ no }}

Databases
: {{ no }}

## Processed Streams

``` mermaid
graph LR
   mx([mx]) -->|kafkasender| kafkasender
```

### Input Streams

| Stream                                             | Description                       |
| -------------------------------------------------- | --------------------------------- |
| [kafkasender](../streams-reference/kafkasender.md) | Messages received from mx service |

## Configuration

`kafkasender` service may be configured via [[kafkasender]](../config-reference/kafkasender.md)
config section.
