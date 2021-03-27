# dispose.POOL Stream

`dispose.POOL` stream is a part of [Events Pipeline](index.md#events-pipeline).
Message processed by [classifier](../../../admin/reference/services/classifier.md) service which may be related with alarm
condition are passed to [correlator](../../../admin/reference/services/correlator.md) service.

Each system [Pool](../../../user/reference/concepts/pool/index.md) has separate
`dispose` stream instance. i.e. `DEFAULT` pool will use `dispose.DEFAULT` stream,
while `CORE` pool will use `dispose.CORE` stream.

## Publishers

- [classifier](../../../admin/reference/services/classifier.md) service.

## Subscribers

- [correlator](../../../admin/reference/services/correlator.md) service.

## Message Headers

`dispose` stream doesn't use additional headers.

## Message Format

`dispose` stream carries JSON-encoded messages.

| Field      | Type                 | Description         |
| ---------- | -------------------- | ------------------- |
| `event_id` | String               | Registered event id |
| `event`    | Object {{ complex }} | Event data          |
