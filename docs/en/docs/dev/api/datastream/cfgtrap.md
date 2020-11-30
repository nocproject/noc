# cfgtrap DataStream

`cfgtrap` [DataStream](index.md) contains configuration
for [services-trapcollector](../../../admin/services/trapcollector.md) service

## Fields

| Name      | Type            | Description                                                |
| --------- | --------------- | ---------------------------------------------------------- |
| id        | String          | [Managed Object's](../../../reference/concepts/managed-object/index.md) id       |
| change_id | String          | [Record's Change Id](index.md#change-id)                   |
| pool      | String          | [Pool's](../../../reference/concepts/pool/index.md)                         |
| fm_pool   | String          | [Pool's](../../../reference/concepts/pool/index.md) for FM event processing |
| addresses | Array of String | List of SNMP Trap sources' IP addresses                    |

## Filters

### pool(name)

Restrict stream to objects belonging to pool `name`

name
: Pool name

## Access
[](../../../reference/concepts/managed-object-profile/index.md)
[API Key](../../../reference/concepts/apikey/index.md) with `datastream:cfgtrap` permissions
required.
