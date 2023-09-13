# vrf DataStream

`vrf` [DataStream](index.md) contains summarized IPAM VRF state

## Fields

| Name                     | Type                 | Description                              |
| ------------------------ | -------------------- | ---------------------------------------- |
| id                       | String               | VRF id                                   |
| change_id                | String               | [Record's Change Id](index.md#change-id) |
| name                     | String               | VRF name                                 |
| vpn_id                   | String               | VPN ID                                   |
| afi                      | Object {{ complex }} | Enabled Address Families                 |
| {{ tab }} ipv4           | Boolean              | IPv4 is enabled on VRF                   |
| {{ tab }} ipv6           | Boolean              | IPv6 is enabled on VRF                   |
| description              | String               | VRF textual description                  |
| rd                       | String               | VRF route distinguisher                  |
| tags                     | Array of String      | VRF tags                                 |
| state                    | Object {{ complex }} | VRF workflow state                       |
| {{ tab }} id             | String               | State id                                 |
| {{ tab }} name           | String               | State name                               |
| {{ tab }} workflow       | Object {{ complex }} | VRF workflow                             |
| {{ tab2 }} id            | String               | Workflow id                              |
| {{ tab2 }} name          | String               | Workflow name                            |
| {{ tab }} allocated_till | Datetime             | Workflow state deadline                  |
| profile                  | Object {{ complex }} | VRF Profile                              |
| {{ tab }} id             | String               | VRF Profile id                           |
| {{ tab }} name           | String               | VRF Profile name                         |
| project                  | Object {{ complex }} | VRF Project                              |
| {{ tab }} id             | String               | Project id                               |
| {{ tab }} name           | String               | Project name                             |
| source                   | String               | VRF Learning source:                     |
|                          |                      | &bull; `M` - Manual                      |
|                          |                      | &bull; `i` - Interface                   |
|                          |                      | &bull; `m` - MPLS                        |
|                          |                      | &bull; `c` - ConfDB                      |

## Access

[API Key](../concepts/apikey/index.md) with `datastream:vrf` permissions
required.
