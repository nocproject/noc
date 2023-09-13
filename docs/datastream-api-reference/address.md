# address DataStream

`address` [DataStream](index.md) contains summarized IPAM Address state

## Fields

| Name                     | Type                 | Description                              |
| ------------------------ | -------------------- | ---------------------------------------- |
| id                       | String               | Address id                               |
| change_id                | String               | [Record's Change Id](index.md#change-id) |
| name                     | String               | Address name                             |
| address                  | String               | Address (i.e. `192.168.0.1`)             |
| fqdn                     | String               | Fully-Qualified Domain Name for address  |
| afi                      | String               | Address family:                          |
|                          |                      | &bull; `ipv4`                            |
|                          |                      | &bull; `ipv6`                            |
| description              | String               | Address textual description              |
| mac                      | String               | Related MAC address                      |
| subinterface             | String               | Related subinterface name                |
| tags                     | Array of String      | VRF tags                                 |
| state                    | Object {{ complex }} | VRF workflow state                       |
| {{ tab }} id             | String               | State id                                 |
| {{ tab }} name           | String               | State name                               |
| {{ tab }} workflow       | Object {{ complex }} | VRF workflow                             |
| {{ tab2 }} id            | String               | Workflow id                              |
| {{ tab2 }} name          | String               | Workflow name                            |
| {{ tab }} allocated_till | Datetime             | Workflow state deadline                  |
| profile                  | Object {{ complex }} | Address Profile                          |
| {{ tab }} id             | String               | Address Profile id                       |
| {{ tab }} name           | String               | Address Profile name                     |
| vrf                      | Object {{ complex }} | Prefix VRF                               |
| {{ tab }} id             | String               | VRF id                                   |
| {{ tab }} name           | String               | VRF name                                 |
| project                  | Object {{ complex }} | Address Project                          |
| {{ tab }} id             | String               | Project id                               |
| {{ tab }} name           | String               | Project name                             |
| source                   | String               | VRF Learning source:                     |
|                          |                      | &bull; `M` - Manual                      |
|                          |                      | &bull; `i` - Interface                   |
|                          |                      | &bull; `m` - Management                  |
|                          |                      | &bull; `d` - DHCP                        |
|                          |                      | &bull; `n` - Neighbor                    |

## Access

[API Key](../concepts/apikey/index.md) with `datastream:address` permission
is required.
