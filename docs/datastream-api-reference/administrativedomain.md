# administrativedomain DataStream

`administrativedomain` [DataStream](index.md) contains summarized
[Administrative Domain](../concepts/administrative-domain/index.md)
state

## Fields

| Name   | Type            | Description                                                              |
| ------ | --------------- | ------------------------------------------------------------------------ |
| id     | String          | [Administrative Domain's](../concepts/administrative-domain/index.md) ID |
| name   | String          | Name                                                                     |
| parent | String          | Parent's ID (if exists)                                                  |
| tags   | Array of String | List of tags                                                             |

## Access

[API Key](../concepts/apikey/index.md) with `datastream:administrativedomain` permissions
required.
