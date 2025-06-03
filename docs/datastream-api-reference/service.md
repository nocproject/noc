# address DataStream

`service` [DataStream](index.md) contains summarized Services state

## Fields

| Name                     | Type                          | Description                                                           |
|--------------------------|-------------------------------|-----------------------------------------------------------------------|
| id                       | String                        | Service Id                                                            |
| remote_system            | Object {{ complex }}          | Source [remote system](../concepts/remote-system/index.md) for object |
| {{ tab }} id             | String                        | External system's Id                                                  |
| {{ tab }} name           | String                        | External system's name                                                |
| remote_id                | String                        | External system's Id (Opaque atribute)                                |
| bi_id                    | Integer                       | BI Database id (metrics)                                              |
| change_id                | String                        | [Record's Change Id](index.md#change-id)                              |
| parent                   | String                        | Parent's ID (if exists)                                               |
| label                    | String                        | Service text lable                                                    |
| description              | String                        | Service textual description                                           |
| address                  | String                        | Service textual location string                                       |
| agreement_id             | String                        | Service textual Agreement                                             |
| labels                   | Array of String               | Service labels (tags)                                                 |
| state                    | Object {{ complex }}          | Service workflow state                                                |
| {{ tab }} id             | String                        | State Id                                                              |
| {{ tab }} name           | String                        | State name                                                            |
| {{ tab }} workflow       | Object {{ complex }}          | Service workflow                                                      |
| {{ tab2 }} id            | String                        | Workflow Id                                                           |
| {{ tab2 }} name          | String                        | Workflow name                                                         |
| {{ tab }} allocated_till | Datetime                      | Workflow state deadline                                               |
| profile                  | Object {{ complex }}          | Service Profile                                                       |
| {{ tab }} id             | String                        | Service Profile Id                                                    |
| {{ tab }} name           | String                        | Service Profile name                                                  |
| project                  | Object {{ complex }}          | Service Project                                                       |
| {{ tab }} id             | String                        | Project id                                                            |
| {{ tab }} name           | String                        | Project name                                                          |
| capabilities             | Array of Object {{ complex }} | List of object's [capabilities](#caps)                                |
| {{ tab }} name           | String                        | Capability's name                                                     |
| {{ tab }} value          | String                        | Capabbility's value                                                   |
| service_groups           | Array of Object {{ complex }} | Service [Resource Groups](../concepts/resource-group/index.md)        |
| {{ tab }} id             | String                        | [Resource Group's](../concepts/resource-group/index.md) id            |
| {{ tab }} name           | String                        | [Resource Group's](../concepts/resource-group/index.md) id            |
| {{ tab }} technology     | String                        | [Technology's](../concepts/technology/index.md) name                  |
| {{ tab }} static         | Boolean                       | true if group is static                                               |
| client_groups            | Array of Object {{ complex }} | Client [Resource Groups](../concepts/resource-group/index.md)         |
| {{ tab }} id             | String                        | [Resource Group's](../concepts/resource-group/index.md) id            |
| {{ tab }} name           | String                        | [Resource Group's](../concepts/resource-group/index.md) id            |
| {{ tab }} technology     | String                        | [Technology's](../concepts/technology/index.md) name                  |
| {{ tab }} static         | Boolean                       | true if group is static                                               |

## Access

[API Key](../concepts/apikey/index.md) with `datastream:service` permission
is required.
