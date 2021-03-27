---
uuid: 16c2b30a-4378-40ae-889f-c78e09f5c335
---
# Config | Config Sync Failed

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
config | Config type | {{ no }}

## Alarm Correlation

Scheme of correlation of `Config | Config Sync Failed` alarms with other alarms is on the chart. 
Arrows are directed from root cause to consequences.

```mermaid
graph TD
  A[["Config | Config Sync Failed"]]
  R1["Chassis | Stack | Stack Degraded"]
  R2["Chassis | Supervisor | Supervisor Down"]
  R1 --> A
  R2 --> A
```

### Root Causes
`Config | Config Sync Failed` alarm may be consequence of

Alarm Class | Description
--- | ---
[Chassis \| Stack \| Stack Degraded](../chassis/stack/stack-degraded.md) | Stack Degraded
[Chassis \| Supervisor \| Supervisor Down](../chassis/supervisor/supervisor-down.md) | Supervisor Down
