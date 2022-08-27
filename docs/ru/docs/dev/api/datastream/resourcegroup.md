---
tags:
  - reference
  - api
---
# resourcegroup DataStream

`resourcegroup` [DataStream](index.md) contains summarized [Resource Group](../../../user/reference/concepts/resource-group/index.md)
state

## Fields

| Name           | Type                 | Description                                                        |
| -------------- | -------------------- | ------------------------------------------------------------------ |
| id             | String               | [Administrative Domain's](../../../user/reference/concepts/administrative-domain/index.md) ID |
| name           | String               | Name                                                               |
| parent         | String               | Parent's ID (if exists)                                            |
| technology     | Object {{ complex }} | Resource Group's [Technology](../../../user/reference/concepts/technology/index.md)           |
| remote_system  | Object {{ complex }} | Source [remote system](../../../user/reference/concepts/remote-system/index.md) for object    |
| {{ tab }} id   | String               | External system's id                                               |
| {{ tab }} name | String               | External system's name                                             |
| remote_id      | String               | External system's id (Opaque attribute)                            |

## Access

[API Key](../../../user/reference/concepts/apikey/index.md) with `datastream:resourcegroup` permissions
required.
