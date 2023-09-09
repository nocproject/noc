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
[icmp_rtt](../types/sla/icmp-rtt.md) | UInt32 | [SLA \| ICMP RTT](../types/sla/icmp-rtt.md)
[jitter](../types/sla/jitter.md) | Int32 | [SLA \| JITTER](../types/sla/jitter.md)
[loss](../types/sla/loss.md) | UInt32 | [SLA \| LOSS](../types/sla/loss.md)
[udp_rtt](../types/sla/udp-rtt.md) | UInt32 | [SLA \| UDP RTT](../types/sla/udp-rtt.md)
