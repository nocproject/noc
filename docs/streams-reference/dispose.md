# dispose.POOL Stream

`dispose.POOL` stream is a part of [Events Pipeline](index.md#events-pipeline).
Message processed by [classifier](../services-reference/classifier.md) service which may be related with alarm
condition are passed to [correlator](../services-reference/correlator.md) service.

Each system [Pool](../concepts/pool/index.md) has separate
`dispose` stream instance. i.e. `DEFAULT` pool will use `dispose.DEFAULT` stream,
while `CORE` pool will use `dispose.CORE` stream.

## Publishers

- [classifier](../services-reference/classifier.md) service.
- [discovery](../services-reference/discovery.md) service.
- [ping](../services-reference/ping.md) service.

## Subscribers

- [correlator](../services-reference/correlator.md) service.

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
| `event`    | Object {{ complex }} | Event data          |

### raise message
`raise` message represents a direct alarm rising request, issued by an external mechanism.

| Field                   | Type                          | Description                                                                                                  |
| ----------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `$op`                   | String                        | Equals to `raise`                                                                                            |
| `reference`             | String                        | Alarm reference. See [alarm reference format](../alarm-reference-format/index.md) for details                |
| `timestamp`             | String                        | Optional timestamp in ISO 8601 format                                                                        |
| `managed_object`        | String                        | Managed Object'd ID. If prefixed with `bi_id:` use BI ID.                                                    |
| `alarm_class`           | String                        | Alarm class name                                                                                             |
| `groups`                | Array of Object {{ complex }} | Optional static groups                                                                                       |
| {{ tab }} `reference`   | String                        | Optional Group Alarm reference. See [alarm reference format](../alarm-reference-format/index.md) for details |
| {{ tab }} `name`        | String                        | Optional group name                                                                                          |
| {{ tab }} `alarm_class` | String                        | Optional group alarm class name                                                                              |
| `vars`                  | Object {{ complex }}          | Alarm variables                                                                                              |
| `labels`                | Array of String               | Optional list of alarm labels                                                                                |
| `remote_system`         | String                        | Optional Remote System ID                                                                                    |
| `remote_id`             | String                        | Optional Remote ID                                                                                           |

### clear message
`clear` message represents a direct alarm clear request, issued by an external mechanism.

| Field       | Type   | Description                                                                         |
| ----------- | ------ | ----------------------------------------------------------------------------------- |
| `$op`       | String | Equals to `clear`                                                                   |
| `reference` | String | Alarm reference. Should be the same as in previous [raise](#raise-message) message. |
| `timestamp` | String | Optional timestamp in ISO 8601 format                                               |

### clearid message

`clearid` message represents a direct alarm clear request, issued by an external mechanism.

| Field       | Type   | Description                           |
| ----------- | ------ | ------------------------------------- |
| `$op`       | String | Equals to `clearid`                   |
| `id`        | String | Alarm id                              |
| `timestamp` | String | Optional timestamp in ISO 8601 format |
| `message`   | String | Optional closing message              |
| `source`    | String | Optional closing source/user          |

### ensure_group message
`ensure_group` message creates and synchronizes group with given set of alarms.

| Field                      | Type                         | Descriptionn                                                                                  |
| -------------------------- | ---------------------------- | --------------------------------------------------------------------------------------------- |
| `$op`                      | String                       | Equals to `ensure_group`                                                                      |
| `reference`                | String                       | Alarm reference. See [alarm reference format](../alarm-reference-format/index.md) for details |
| `name`                     | String                       | Group alarm title                                                                             |
| `alarm_class`              | String                       | Optional group alarm class                                                                    |
| `labels`                   | Array of String              | Optional list of group alarm labels                                                           |
| `alarms`                   | Array of Object {{ complex}} | List of active alarms                                                                         |
| {{ tab }} `reference`      | String                       | Alarm reference. See [alarm reference format](../alarm-reference-format/index.md) for details |
| {{ tab }} `timestamp`      | String                       | Optional timestamp in ISO 8601 format                                                         |
| {{ tab }} `managed_object` | String                       | Managed Object'd ID                                                                           |
| {{ tab }} `alarm_class`    | String                       | Alarm class name                                                                              |
| {{ tab }} `vars`           | Object {{ complex }}         | Alarm variables                                                                               |
| {{ tab }} `labels`         | Array of String              | Optional list of alarm labels                                                                 |

