---
tags:
  - reference
  - api
---
# cfgtrap DataStream

`cfgtrap` [DataStream](index.md) contains configuration
for [services-trapcollector](../../../admin/reference/services/trapcollector.md) service

## Fields

| Name      | Type            | Description                                                |
| --------- | --------------- | ---------------------------------------------------------- |
| id        | String          | [Managed Object's](../../../user/reference/concepts/managed-object/index.md) id       |
| change_id | String          | [Record's Change Id](index.md#change-id)                   |
| pool      | String          | [Pool's](../../../user/reference/concepts/pool/index.md)                         |
| fm_pool   | String          | [Pool's](../../../user/reference/concepts/pool/index.md) for FM event processing |
| addresses | Array of String | List of SNMP Trap sources' IP addresses                    |

## Filters

### pool(name)

Restrict stream to objects belonging to pool `name`

name
: Pool name

## Access
[](../../../user/reference/concepts/managed-object-profile/index.md)
[API Key](../../../user/reference/concepts/apikey/index.md) with `datastream:cfgtrap` permissions
required.
