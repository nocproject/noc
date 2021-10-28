# dispose.POOL Stream

`dispose.POOL` stream is a part of [Events Pipeline](index.md#events-pipeline).
Message processed by [classifier](../../../admin/reference/services/classifier.md) service which may be related with alarm
condition are passed to [correlator](../../../admin/reference/services/correlator.md) service.

Each system [Pool](../../../user/reference/concepts/pool/index.md) has separate
`dispose` stream instance. i.e. `DEFAULT` pool will use `dispose.DEFAULT` stream,
while `CORE` pool will use `dispose.CORE` stream.

## Publishers

- [classifier](../../../admin/reference/services/classifier.md) service.
- [discovery](../../../admin/reference/services/discovery.md) service.
- [ping](../../../admin/reference/services/ping.md) service.

## Subscribers

- [correlator](../../../admin/reference/services/correlator.md) service.

## Message Headers

`dispose` stream doesn't use additional headers.

## Message Format

`dispose` stream carries JSON-encoded messages of several types. The type of message is encoded
in the `$op` field. Unknown message types and malformed messages are discarded.

### event message

`event` messages represent classified events that may raise and clear alarms.

| Field      | Type                 | Description         |
| ---------- | -------------------- | ------------------- |
| `$op`      | String               | Equals to `event`   |
| `event_id` | String               | Registered event id |
| `hint`     | Object {{ complex }} | Event data          |

### raise message
`raise` message represents a direct alarm rising request, issued by an external mechanism.

| Field            | Type                 | Description                                                                             |
| ---------------- | -------------------- | --------------------------------------------------------------------------------------- |
| `$op`            | String               | Equals to `raise`                                                                       |
| `reference`      | String               | Alarm reference. See [alarm reference format](../alarm-reference-format.md) for details |
| `timestamp`      | String               | Optional timestamp in ISO 8601 format                                                   |
| `managed_object` | String               | Managed Object'd ID                                                                     |
| `alarm_class`    | String               | Alarm class name                                                                        |
| `vars`           | Object {{ comples }} | Alarm variables                                                                         |
| `remote_system`  | String               | Optional Remote System ID                                                               |
| `remote_id`      | String               | Optional Remote ID                                                                      |

### clear message
`clear` message represents a direct alarm clear request, issued by an external mechanism.

| Field       | Type   | Description                                                                         |
| ----------- | ------ | ----------------------------------------------------------------------------------- |
| `$op`       | String | Equals to `clear`                                                                   |
| `reference` | String | Alarm reference. Should be the same as in previous [raise](#raise-message) message. |
| `timestamp` | String | Optional timestamp in ISO 8601 format                                               |