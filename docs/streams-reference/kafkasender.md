# kafkasender stream

kafkasender stream is a part of [GMX Pipeline](index.md#generic-message-exchange-pipeline).
Outbound messages directed to the external Kafka cluster are routed into
`kafkasender` stream by [mx](../services-reference/mx.md) service.

## Publishers

- [mx](../services-reference/mx.md) service

## Subscribers

- [kafkasender](../services-reference/kafkasender.md) service

## Message Headers

To
: Kafka topic name

Sharding-Key
: Key for consistent sharding.

Kafka_partition
: Kafka partition numbers. You can write some partitional separate by ',' in this case  will load balance between partitional. Example: 0,1,2

## Message Format

`kafkasender` stream does not enforce a specific format. Messages are passed
to external Kafka system as-is.
