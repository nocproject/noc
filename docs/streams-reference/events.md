# events.POOL Stream

`events.POOL` stream is a part of [Events Pipeline](index.md#events-pipeline).
Registered events are passed in unified way from various collectors
to classifier service for further analysis.

Each system [Pool](../concepts/pool/index.md) has separate
`events` stream instance. i.e. `DEFAULT` pool will use `events.DEFAULT` stream,
while `CORE` pool will use `events.CORE` stream.

## Publishers

- [ping](../services-reference/ping.md) service.
- [syslogcollector](../services-reference/syslogcollector.md) service.
- [trapcollector](../services-reference/trapcollector.md) service.

## Subscribers

- [classifier](../services-reference/classifier.md) service.

## Message Headers

`events` stream doesn't use additional headers.

## Message Format

`events` stream carries JSON-encoded messages.

| Field                 | Type                 | Description                            |
| --------------------- | -------------------- | -------------------------------------- |
| `ts`                  | Integer              | Event timestamp, UNIX epoch            |
| `object`              | Integer              | Managed Object Id                      |
| `data`                | Object {{ complex }} | Message Data                           |
| {{ tab }} `source`    | String               | Message source:                        |
| {{ tab }} `source`    | String               | Message source:                        |
|                       |                      | ping                                   |
|                       |                      | syslog                                 |
|                       |                      | SNMP Trap                              |
| {{ tab }} `collector` | String               | Pool name                              |
| {{ tab }} `message`   | String               | Incoming syslog message, if any        |
| {{ tab }} `<OID>`     | String               | SNMP Trap varbinds in key-value format |
