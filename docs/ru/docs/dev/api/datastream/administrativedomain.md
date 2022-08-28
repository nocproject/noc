---
tags:
  - reference
---
# administrativedomain DataStream

`administrativedomain` [DataStream](index.md) contains summarized
[Administrative Domain](../../../user/reference/concepts/administrative-domain/index.md)
state

## Fields

| Name   | Type            | Description                                                                              |
| ------ | --------------- | ---------------------------------------------------------------------------------------- |
| id     | String          | [Administrative Domain's](../../../user/reference/concepts/administrative-domain/index.md) ID |
| name   | String          | Name                                                                                     |
| parent | String          | Parent's ID (if exists)                                                                  |
| tags   | Array of String | List of tags                                                                             |

## Access

[API Key](../../../user/reference/concepts/apikey/index.md) with `datastream:administrativedomain` permissions
required.
