---
uuid: 59ecc1ac-f151-47d9-b513-c2049f77f1ab
---
# Routing Metric Scope

Scope for L2/L3 protocols metrics

## Data Table

ClickHouse Table: `routing`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
path | Array of String {{ complex }} | Measurement Path
{{ tab }} `vr` | {{ no }} | 
{{ tab }} `instance` | {{ no }} | 
[stp_topology_changes](../types/network/stp/topology-changes.md) | UInt32 | [Network \| STP \| Topology Changes](../types/network/stp/topology-changes.md)
[stp_topology_changes_delta](../types/network/stp/topology-changes/delta.md) | UInt32 | [Network \| STP \| Topology Changes \| Delta](../types/network/stp/topology-changes/delta.md)
