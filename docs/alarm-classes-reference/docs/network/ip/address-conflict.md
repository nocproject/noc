---
uuid: ef2b8f0a-3959-4bce-99b8-5eb5298409b9
---
# Network | IP | Address Conflict

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
ip | Conflicting IP | {{ no }}
mac | MAC | {{ no }}
interface | Interface | {{ no }}

## Alarm Correlation

Scheme of correlation of `Network | IP | Address Conflict` alarms with other alarms is on the chart. 
Arrows are directed from root cause to consequences.

```mermaid
graph TD
  A[["Network | IP | Address Conflict"]]
  R1["Network | IP | Address Conflict"]
  C2["Network | IP | Address Conflict"]
  R1 --> A
  A --> C2
```

### Root Causes
`Network | IP | Address Conflict` alarm may be consequence of

Alarm Class | Description
--- | ---
[Network \| IP \| Address Conflict](address-conflict.md) | Address Conflict

### Consequences
`Network | IP | Address Conflict` alarm may be root cause of

Alarm Class | Description
--- | ---
[Network \| IP \| Address Conflict](address-conflict.md) | Address Conflict

## Events

### Opening Events
`Network | IP | Address Conflict` may be raised by events

Event Class | Description
--- | ---
[Network \| IP \| Address Conflict](../../../event-classes/network/ip/address-conflict.md) | dispose
