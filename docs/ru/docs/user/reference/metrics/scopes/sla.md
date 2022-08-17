---
uuid: c2cb029b-4cda-4187-b92b-386c27ea561f
---
# SLA Metric Scope

SLA-related metrics

## Data Table

ClickHouse Table: `sla`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
path | Array of String {{ complex }} | Measurement Path
{{ tab }} `probe` | {{ no }} | 
{{ tab }} `test` | {{ no }} | 
