# prefix DataStream

`prefix` [DataStream](index.md) contains summarized IPAM Prefix state

## Fields

| Name                     | Type                 | Description                              |
| ------------------------ | -------------------- | ---------------------------------------- |
| id                       | String               | Prefix id                                |
| change_id                | String               | [Record's Change Id](index.md#change-id) |
| name                     | String               | Prefix name                              |
| prefix                   | String               | Prefix (i.e. `192.168.0.0/24`)           |
| vpn_id                   | String               | VPN ID                                   |
| afi                      | String               | Prefix address family:                   |
|                          |                      |                                          |
|                          |                      | &bull; `ipv4`                            |
|                          |                      | &bull; `ipv6`                            |
| description              | String               | Prefix textual description               |
| tags                     | Array of String      | Prefix tags                              |
| state                    | Object {{ complex }} | Prefix workflow state                    |
| {{ tab }} id             | String               | State id                                 |
| {{ tab }} name           | String               | State name                               |
| {{ tab }} workflow       | Object {{ complex }} | Prefix workflow                          |
| {{ tab2 }} id            | String               | Workflow id                              |
| {{ tab2 }} name          | String               | Workflow name                            |
| {{ tab }} allocated_till | Datetime             | Workflow state deadline                  |
| profile                  | Object {{ complex }} | Prefix Profile                           |
| {{ tab }} id             | String               | Prefix Profile id                        |
| {{ tab }} name           | String               | Prefix Profile name                      |
| project                  | Object {{ complex }} | Prefix Project                           |
| {{ tab }} id             | String               | Project id                               |
| {{ tab }} name           | String               | Project name                             |
| vrf                      | Object               | Prefix VRF                               |
| {{ tab }} id             | String               | VRF id                                   |
| {{ tab }} name           | String               | VRF name                                 |
| asn                      | Object {{ complex }} | Prefix Autonomous System (AS)            |
| {{ tab }} id             | String               | AS id                                    |
| {{ tab }} name           | String               | AS name                                  |
| {{ tab }} asn            | String               | AS number (like `AS65000`)               |
| source                   | String               | VRF Learning source:                     |
|                          |                      |                                          |
|                          |                      | &bull; `M` - Manual                      |
|                          |                      | &bull; `i` - Interface                   |
|                          |                      | &bull; `w` - Whois                       |
|                          |                      | &bull; `n` - Neighbor                    |

## Access

[API Key](../concepts/apikey/index.md) with `datastream:prefix` permissions
required.
