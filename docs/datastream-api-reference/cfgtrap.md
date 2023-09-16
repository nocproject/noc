# cfgtrap DataStream

`cfgtrap` [DataStream](index.md) contains configuration
for [services-trapcollector](../services-reference/trapcollector.md) service

## Fields

| Name      | Type            | Description                                                 |
| --------- | --------------- | ----------------------------------------------------------- |
| id        | String          | [Managed Object's](../concepts/managed-object/index.md) id  |
| change_id | String          | [Record's Change Id](index.md#change-id)                    |
| pool      | String          | [Pool's](../concepts/pool/index.md)                         |
| fm_pool   | String          | [Pool's](../concepts/pool/index.md) for FM event processing |
| addresses | Array of String | List of SNMP Trap sources' IP addresses                     |

## Filters

### pool(name)

Restrict stream to objects belonging to pool `name`

name
: Pool name

## Access
[](../concepts/managed-object-profile/index.md)
[API Key](../concepts/apikey/index.md) with `datastream:cfgtrap` permissions
required.
