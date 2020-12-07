---
uuid: 16f51199-4c36-477c-b311-2110a87666a0
---
# System | Reboot

## Symptoms

## Probable Causes

## Recommended Actions

## Alarm Correlation

Scheme of correlation of `System | Reboot` alarms with other alarms is on the chart. 
Arrows are directed from root cause to consequences.

```mermaid
graph TD
  A[["System | Reboot"]]
  C1["NOC | Managed Object | Ping Failed"]
  A --> C1
```

### Consequences
`System | Reboot` alarm may be root cause of

Alarm Class | Description
--- | ---
[NOC \| Managed Object \| Ping Failed](../noc/managed-object/ping-failed.md) | System Reboot

## Events

### Opening Events
`System | Reboot` may be raised by events

Event Class | Description
--- | ---
[System \| Reboot](../../event-classes/system/reboot.md) | dispose

### Closing Events
`System | Reboot` may be cleared by events

Event Class | Description
--- | ---
[System \| Started](../../event-classes/system/started.md) | dispose
