# address DataStream

`service` [DataStream](index.md) contains summarized Services state

## Fields

| Name                     | Type                          | Description                                                           |
|--------------------------|-------------------------------|-----------------------------------------------------------------------|
| id                       | String                        | Service Id                                                            |
| remote_system            | Object {{ complex }}          | Source [remote system](../concepts/remote-system/index.md) for object |
| {{ tab }} id             | String                        | External system's Id                                                  |
| {{ tab }} name           | String                        | External system's name                                                |
| remote_id                | String                        | External system's Id                                                  |
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
| remote_mappings          | Array of Object {{ complex }} | List of object's Mapping on Remote System                             |
| {{ tab }} remote_system  | Object {{ complex }}          | Source [remote system](../concepts/remote-system/index.md) for object |
| {{ tab2 }} id            | String                        | External system's Id                                                  |
| {{ tab2 }} name          | String                        | External system's name                                                |
| {{ tab }} remote_id      | String                        | External system's Id                                                  |

## Access

[API Key](../concepts/apikey/index.md) with `datastream:service` permission
is required.

## Example

```json
{
  "id": "679f5f17e161988989c93d96",
  "$version": 1,
  "label": "Service 22",
  "bi_id": 472041709300745497,
  "description": "running tests",
  "state": {
    "id": "606eaffbd179a5da7e340a41",
    "name": "Unknown",
    "workflow": {
      "id": "606eafb1d179a5da7e340a3f",
      "name": "Service Default"
    }
  },
  "profile": {
    "id": "671f147709d1a15ecb9de072",
    "name": "Тестовый сервис"
  },
  "remote_system": {
    "id": "6650686f8c0b81d06271a4f1",
    "name": "TEST"
  },
  "remote_id": "TEST-1234",
  "remote_mappings": [
    {
      "id": "6650686f8c0b81d06271a4f1",
      "name": "TEST"
    },
    {
      "remote_system": {
        "id": "683e7d76f439370ad7957d5c",
        "name": "X-TEST"
      },
      "remote_id": "1234556"
    }
  ],
  "effective_remote_map": {
    "TEST": "TEST-1234",
    "X-TEST": "1234556"
  },
  "change_id": "683eaa219a169cb98a854d7a"
}

```