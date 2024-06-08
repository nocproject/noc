# cfgmetrics DataStream

`cfgmetrics` [DataStream](index.md) contains configuration
for [metricscollector](../services-reference/metricscollector.md) service

## Fields

| Name                 | Type            | Description                                              |
| -------------------- | --------------- | -------------------------------------------------------- |
| id                   | String          | item id                                                  |
| change_id            | String          | [Record's Change Id](index.md#change-id)                 |
| table                | String          | ClickHouse table name                                    |
| field                | String          | ClickHouse field name                                    |
| rules                | Array of Object | Mapping rules                                            |
| {{ tab }} collector  | String          | [Collector](../agent-reference/collectors/index.md) name |
| {{ tab }} field      | String          | Collector's output field                                 |
| {{ tab }} labels     | Array of String | List of matching labels                                  |
| {{ tab }} preference | Integer         | Rule preference (less is preferable)                     |

## Access

[API Key](../concepts/apikey/index.md) with `datastream:cfgmentrics` permissions
required.
