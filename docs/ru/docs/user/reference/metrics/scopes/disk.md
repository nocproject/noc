---
uuid: c34050a3-d456-432e-9ec2-945547ca9096
---
# Disk Metric Scope

Disk metrics

## Data Table

ClickHouse Table: `disk`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
path | Array of String {{ complex }} | Measurement Path
{{ tab }} `path` | {{ no }} | 
[disk_usage_b](../types/disk/usage.md) | UInt64 | [Disk \| Usage](../types/disk/usage.md)
[disk_usage_p](../types/disk/usage-percent.md) | UInt8 | [Disk \| Usage Percent](../types/disk/usage-percent.md)
