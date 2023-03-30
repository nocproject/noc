---
uuid: f5da2fd6-f712-43f1-b788-16812f844239
---
# Network | UDLD | UDLD Protocol Error Detected

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
interface | interface | {{ no }}
description | Interface description | `=InterfaceDS.description`

## Alarm Correlation

Scheme of correlation of `Network | UDLD | UDLD Protocol Error Detected` alarms with other alarms is on the chart. 
Arrows are directed from root cause to consequences.

```mermaid
graph TD
  A[["Network | UDLD | UDLD Protocol Error Detected"]]
  C1["Network | Link | Err-Disable"]
  A --> C1
```

### Consequences
`Network | UDLD | UDLD Protocol Error Detected` alarm may be root cause of

Alarm Class | Description
--- | ---
[Network \| Link \| Err-Disable](../link/err-disable.md) | UDLD

## Events

### Opening Events
`Network | UDLD | UDLD Protocol Error Detected` may be raised by events

Event Class | Description
--- | ---
[Network \| UDLD \| UDLD Protocol Error Detected](../../../event-classes/network/udld/udld-protocol-error-detected.md) | dispose

### Closing Events
`Network | UDLD | UDLD Protocol Error Detected` may be cleared by events

Event Class | Description
--- | ---
[Network \| UDLD \| UDLD Protocol Recovery](../../../event-classes/network/udld/udld-protocol-recovery.md) | dispose
