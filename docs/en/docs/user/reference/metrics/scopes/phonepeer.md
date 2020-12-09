---
uuid: 77d6efee-a07d-4c85-a7e6-06e831e2196a
---
# PhonePeer Metric Scope

Scope for Pphone Peer protocols metrics (SIP Trunk, E1 Serial, etc.) . Explain:
trunk as interface
channel as subinterface

## Data Table

ClickHouse Table: `phonepeer`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
path | Array of String {{ complex }} | Measurement Path
{{ tab }} `trunk` | {{ no }} | 
{{ tab }} `channel` | {{ no }} | 
