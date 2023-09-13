---
uuid: c34050a3-d456-432e-9ec2-945547ca9096
---
# Disk Metric Scope

Disk metrics

## Data Table

ClickHouse Table: `disk`

| Field                                                           | Type                          | Description                                                              |
| --------------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------ |
| date                                                            | Date                          | Measurement Date                                                         |
| ts                                                              | DateTime                      | Measurement Timestamp                                                    |
| path                                                            | Array of String {{ complex }} | Measurement Path                                                         |
| {{ tab }} `path`                                                | {{ no }}                      |
| [disk_usage_b](../metric-types-reference/disk/usage.md)         | UInt64                        | [Disk \| Usage](../metric-types-reference/disk/usage.md)                 |
| [disk_usage_p](../metric-types-reference/disk/usage-percent.md) | UInt8                         | [Disk \| Usage Percent](../metric-types-reference/disk/usage-percent.md) |
