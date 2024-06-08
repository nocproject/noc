# cfgping DataStream

`cfgping` [DataStream](index.md) contains configuration
for [ping](../services-reference/ping.md) service

## Fields

| Name            | Type    | Description                                                                 |
| --------------- | ------- | --------------------------------------------------------------------------- |
| id              | String  | [Managed Object's](../concepts/managed-object/index.md) id                  |
| change_id       | String  | [Record's Change Id](index.md#change-id)                                    |
| pool            | String  | [Pool's](../concepts/pool/index.md) name                                    |
| fm_pool         | String  | [Pool's](../concepts/pool/index.md) for FM event processing                 |
| interval        | Integer | Probing rounds interval in seconds                                          |
| policy          | String  | Probing policy:                                                             |
|                 |         | \* f - Success on first successful try                                      |
|                 |         | \* a - Success only if all tries successful                                 |
| size            | Integer | ICMP Echo-Request packet size                                               |
| count           | Integer | Probe attempts per round                                                    |
| timeout         | Integer | Probe timeout in seconds                                                    |
| expr_policy     | String  | Free time behaviour:                                                        |
|                 |         | D - furn off pinging                                                        |
|                 |         | E - continue pinging, but don't follow status                               |
| report_rtt      | Boolean | Report [Ping RTT](../metrics-reference/index.md) metric per each round      |
| report_attempts | Boolean | Report [Ping Attempts](../metrics-reference/index.md) metric per each round |
| status          | Null    | Reserved                                                                    |
| name            | String  | [Managed Object's](../concepts/managed-object/index.md) name                |
| bi_id           | Integer | [Managed Object's](../concepts/managed-object/index.md) BI Id               |

<!-- prettier-ignore -->
!!! todo
    Add BI ID reference

## Filters

### pool(name)

Restrict stream to objects belonging to pool `name`

name
: Pool name

## Access

[API Key](../concepts/apikey/index.md) with `datastream:cfgping` permissions
required.
