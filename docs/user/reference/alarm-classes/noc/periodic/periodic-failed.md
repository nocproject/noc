---
uuid: 19331749-daac-435d-829c-b9fedf85603f
---
# NOC | Periodic | Periodic Failed

## Symptoms

No specific symptoms

## Probable Causes

Failure occured when noc-scheduler tried to execute periodic task

## Recommended Actions

Check noc-scheduler, noc-sae and noc-activator logs

## Variables

Variable | Description | Default
--- | --- | ---
task | Task name | {{ no }}

## Events

### Opening Events
`NOC | Periodic | Periodic Failed` may be raised by events

Event Class | Description
--- | ---
[NOC \| Periodic \| Periodic Failed](../../../event-classes/noc/periodic/periodic-failed.md) | dispose

### Closing Events
`NOC | Periodic | Periodic Failed` may be cleared by events

Event Class | Description
--- | ---
[NOC \| Periodic \| Periodic OK](../../../event-classes/noc/periodic/periodic-ok.md) | dispose
