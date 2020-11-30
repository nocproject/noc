# cfgsyslog DataStream

`cfgsyslog` [DataStream](index.md) contains configuration
for [syslogcollector](../../../admin/services/syslogcollector.md) service

## Fields

| Name      | Type            | Description                                                |
| --------- | --------------- | ---------------------------------------------------------- |
| id        | String          | [Managed Object's](../../../reference/concepts/managed-object/index.md) id       |
| change_id | String          | [Record's Change Id](index.md#change-id)                   |
| pool      | String          | [Pool's](../../../reference/concepts/pool/index.md)                         |
| fm_pool   | String          | [Pool's](../../../reference/concepts/pool/index.md) for FM event processing |
| addresses | Array of String | List of syslog sources' IP addresses                       |

## Filters

### pool(name)

Restrict stream to objects belonging to pool `name`

name
: Pool name

## Access

[API Key](../../../reference/concepts/apikey/index.md) with `datastream:cfgsyslog` permissions
required.
