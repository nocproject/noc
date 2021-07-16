---
uuid: 34ceeb58-db4a-401b-a98b-0a446ad8f4bb
---
# Vendor | f5 | BIGIP | Network | Load Balance | Node Down

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
node | IP or hostname | {{ no }}

## Alarm Correlation

Scheme of correlation of `Vendor | f5 | BIGIP | Network | Load Balance | Node Down` alarms with other alarms is on the chart. 
Arrows are directed from root cause to consequences.

```mermaid
graph TD
  A[["Vendor | f5 | BIGIP | Network | Load Balance | Node Down"]]
  C1["Vendor | f5 | BIGIP | Network | Load Balance | Service Down"]
  A --> C1
```

### Consequences
`Vendor | f5 | BIGIP | Network | Load Balance | Node Down` alarm may be root cause of

Alarm Class | Description
--- | ---
[Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Service Down](service-down.md) | Node down

## Events

### Opening Events
`Vendor | f5 | BIGIP | Network | Load Balance | Node Down` may be raised by events

Event Class | Description
--- | ---
[Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Node Down](../../../../../../event-classes/vendor/f5/bigip/network/load-balance/node-down.md) | dispose

### Closing Events
`Vendor | f5 | BIGIP | Network | Load Balance | Node Down` may be cleared by events

Event Class | Description
--- | ---
[Vendor \| f5 \| BIGIP \| Network \| Load Balance \| Node Up](../../../../../../event-classes/vendor/f5/bigip/network/load-balance/node-up.md) | dispose
