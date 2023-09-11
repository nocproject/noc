---
uuid: 3e164372-199a-45c7-bda4-177b6b5c853a
---
# VPN Metric Scope

Metrics for L2/L3 vpn tunnels.
Instance - VPN ID: use it for L2 VPN name
local_endpoint and remote_endpoint: For IPSEC it contains local IP and remote IP, for other type some string


## Data Table

ClickHouse Table: `vpns`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
path | Array of String {{ complex }} | Measurement Path
{{ tab }} `instance` | {{ no }} | 
{{ tab }} `local_endpoint` | {{ no }} | 
{{ tab }} `remote_endpoint` | {{ no }} | 
