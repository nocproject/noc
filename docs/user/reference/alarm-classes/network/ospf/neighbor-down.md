---
uuid: 7bd05776-7d5e-4eae-9401-2e45e290756f
---
# Network | OSPF | Neighbor Down

## Symptoms

Routing table changes and possible lost of connectivity

## Probable Causes

Link failure or protocol misconfiguration

## Recommended Actions

Check links and local and neighbor router configuration

## Variables

Variable | Description | Default
--- | --- | ---
area | OSPF area | {{ no }}
interface | Interface | {{ no }}
neighbor | Neighbor's Router ID | {{ no }}
reason | Adjacency lost reason | {{ no }}
vrf | VRF | {{ no }}
description | Interface description | `=InterfaceDS.description`

## Alarm Correlation

Scheme of correlation of `Network | OSPF | Neighbor Down` alarms with other alarms is on the chart. 
Arrows are directed from root cause to consequences.

```mermaid
graph TD
  A[["Network | OSPF | Neighbor Down"]]
  R1["Network | Link | Link Down"]
  R1 --> A
```

### Root Causes
`Network | OSPF | Neighbor Down` alarm may be consequence of

Alarm Class | Description
--- | ---
[Network \| Link \| Link Down](../link/link-down.md) | Link Down

## Events

### Opening Events
`Network | OSPF | Neighbor Down` may be raised by events

Event Class | Description
--- | ---
[Network \| OSPF \| Neighbor Down](../../../event-classes/network/ospf/neighbor-down.md) | dispose

### Closing Events
`Network | OSPF | Neighbor Down` may be cleared by events

Event Class | Description
--- | ---
[Network \| OSPF \| Neighbor Up](../../../event-classes/network/ospf/neighbor-up.md) | dispose
