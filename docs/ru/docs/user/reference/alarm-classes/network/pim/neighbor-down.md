---
uuid: 3fe312b7-a381-455d-9d8e-50bd2cd1d173
---
# Network | PIM | Neighbor Down

## Symptoms

Multicast flows lost

## Probable Causes

Link failure or protocol misconfiguration

## Recommended Actions

Check links and local and neighbor router configuration

## Variables

Variable | Description | Default
--- | --- | ---
interface | Interface | {{ no }}
neighbor | Neighbor's IP | {{ no }}
vrf | VRF | {{ no }}
reason | Reason | {{ no }}
description | Interface description | `=InterfaceDS.description`

## Alarm Correlation

Scheme of correlation of `Network | PIM | Neighbor Down` alarms with other alarms is on the chart. 
Arrows are directed from root cause to consequences.

```mermaid
graph TD
  A[["Network | PIM | Neighbor Down"]]
  R1["Network | Link | Link Down"]
  R2["Network | BFD | Session Down"]
  R1 --> A
  R2 --> A
```

### Root Causes
`Network | PIM | Neighbor Down` alarm may be consequence of

Alarm Class | Description
--- | ---
[Network \| Link \| Link Down](../link/link-down.md) | Link Down
[Network \| BFD \| Session Down](../bfd/session-down.md) | Link Down

## Events

### Opening Events
`Network | PIM | Neighbor Down` may be raised by events

Event Class | Description
--- | ---
[Network \| PIM \| Neighbor Down](../../../event-classes/network/pim/neighbor-down.md) | dispose

### Closing Events
`Network | PIM | Neighbor Down` may be cleared by events

Event Class | Description
--- | ---
[Network \| PIM \| Neighbor Up](../../../event-classes/network/pim/neighbor-up.md) | dispose
