---
uuid: 201c3a1e-f92d-4c80-b7c3-bf193c678cf1
---
# Memory Metric Scope

Memory-related metrics

## Data Table

ClickHouse Table: `memory`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
path | Array of String {{ complex }} | Measurement Path
{{ tab }} `chassis` | {{ no }} | 
{{ tab }} `slot` | {{ no }} | 
{{ tab }} `module` | {{ no }} | 
[load_1min](../types/memory/load/1min.md) | UInt8 | [Memory \| Load \| 1min](../types/memory/load/1min.md)
[usage](../types/memory/usage.md) | UInt8 | [Memory \| Usage](../types/memory/usage.md)
[usage_5s](../types/memory/usage/5sec.md) | UInt8 | [Memory \| Usage \| 5sec](../types/memory/usage/5sec.md)
