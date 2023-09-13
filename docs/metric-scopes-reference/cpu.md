---
uuid: 8c2c88f3-e00f-4955-83d6-453f97ba3dc4
---
# CPU Metric Scope

CPU-related metrics

## Data Table

ClickHouse Table: `cpu`

| Field                                                   | Type                          | Description                                                         |
| ------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------- |
| date                                                    | Date                          | Measurement Date                                                    |
| ts                                                      | DateTime                      | Measurement Timestamp                                               |
| path                                                    | Array of String {{ complex }} | Measurement Path                                                    |
| {{ tab }} `chassis`                                     | {{ no }}                      |
| {{ tab }} `slot`                                        | {{ no }}                      |
| {{ tab }} `module`                                      | {{ no }}                      |
| {{ tab }} `name`                                        | {{ no }}                      |
| [load_1min](../metric-types-reference/cpu/load/1min.md) | UInt8                         | [CPU \| Load \| 1min](../metric-types-reference/cpu/load/1min.md)   |
| [load_5min](../metric-types-reference/cpu/load/5min.md) | UInt8                         | [CPU \| Load \| 5min](../metric-types-reference/cpu/load/5min.md)   |
| [load_5s](../metric-types-reference/cpu/usage/5sec.md)  | UInt8                         | [CPU \| Usage \| 5sec](../metric-types-reference/cpu/usage/5sec.md) |
| [usage](../metric-types-reference/cpu/usage.md)         | UInt8                         | [CPU \| Usage](../metric-types-reference/cpu/usage.md)              |
