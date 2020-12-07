---
uuid: 52ea3beb-fa6d-40f9-97f0-f3958d0c8089
---
# Network | IS-IS | Adjacency Down

## Symptoms

Routing table changes and possible lost of connectivity

## Probable Causes

Link failure or protocol misconfiguration

## Recommended Actions

Check links and local and neighbor router configuration

## Variables

Variable | Description | Default
--- | --- | ---
interface | Interface | {{ no }}
neighbor | Neighbor's NSAP or name | {{ no }}
level | Level | {{ no }}
reason | Adjacency lost reason | {{ no }}

## Alarm Correlation

Scheme of correlation of `Network | IS-IS | Adjacency Down` alarms with other alarms is on the chart. 
Arrows are directed from root cause to consequences.

```mermaid
graph TD
  A[["Network | IS-IS | Adjacency Down"]]
  R1["Network | Link | Link Down"]
  R2["Network | BFD | Session Down"]
  R1 --> A
  R2 --> A
```

### Root Causes
`Network | IS-IS | Adjacency Down` alarm may be consequence of

Alarm Class | Description
--- | ---
[Network \| Link \| Link Down](../link/link-down.md) | Link Down
[Network \| BFD \| Session Down](../bfd/session-down.md) | Link Down

## Events

### Opening Events
`Network | IS-IS | Adjacency Down` may be raised by events

Event Class | Description
--- | ---
[Network \| IS-IS \| Adjacency Down](../../../event-classes/network/is-is/adjacency-down.md) | dispose

### Closing Events
`Network | IS-IS | Adjacency Down` may be cleared by events

Event Class | Description
--- | ---
[Network \| IS-IS \| Adjacency Up](../../../event-classes/network/is-is/adjacency-up.md) | dispose
