---
uuid: bdc6f9ed-604b-447d-b394-066d2aef9874
---
# Neighbors Metric Scope

Metrics for L2/L3 protocols neighbors

## Data Table

ClickHouse Table: `neighbors`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
path | Array of String {{ complex }} | Measurement Path
{{ tab }} `vr` | {{ no }} | 
{{ tab }} `instance` | {{ no }} | 
{{ tab }} `neighbor` | {{ no }} | 
