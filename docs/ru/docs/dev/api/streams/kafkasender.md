# kafkasender stream

kafkasender stream is a part of [GMX Pipeline](index.md#generic-message-exchange-pipeline).
Outbound messages directed to the external Kafka cluster are routed into
`kafkasender` stream by [mx](../../../admin/reference/services/mx.md) service.

## Publishers

- [mx](../../../admin/reference/services/mx.md) service

## Subscribers

- [kafkasender](../../../admin/reference/services/kafkasender.md) service

## Message Headers

To
: Kafka topic name

Sharding-Key
: Key for consistent sharding.

## Message Format

`kafkasender` stream does not enforce a specific format. Messages are passed
to external Kafka system as-is.
