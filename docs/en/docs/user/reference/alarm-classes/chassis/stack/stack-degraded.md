---
uuid: ed3566d9-75dc-46e6-a012-1c05387cd5dd
---
# Chassis | Stack | Stack Degraded

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
unit | Unit number | {{ no }}

## Alarm Correlation

Scheme of correlation of `Chassis | Stack | Stack Degraded` alarms with other alarms is on the chart. 
Arrows are directed from root cause to consequences.

```mermaid
graph TD
  A[["Chassis | Stack | Stack Degraded"]]
  C1["Config | Config Sync Failed"]
  A --> C1
```

### Consequences
`Chassis | Stack | Stack Degraded` alarm may be root cause of

Alarm Class | Description
--- | ---
[Config \| Config Sync Failed](../../config/config-sync-failed.md) | Stack Degraded

## Events

### Opening Events
`Chassis | Stack | Stack Degraded` may be raised by events

Event Class | Description
--- | ---
[Chassis \| Stack \| Stack Degraded](../../../event-classes/chassis/stack/stack-degraded.md) | dispose

### Closing Events
`Chassis | Stack | Stack Degraded` may be cleared by events

Event Class | Description
--- | ---
[Chassis \| Stack \| Stack is Raised](../../../event-classes/chassis/stack/stack-is-raised.md) | dispose
