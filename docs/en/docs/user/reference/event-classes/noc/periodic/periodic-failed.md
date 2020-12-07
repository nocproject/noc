---
uuid: 919bf2f9-bc5e-43a1-8df8-f462ab4ea025
---
# NOC | Periodic | Periodic Failed

Periodic task has been failed

## Symptoms

No specific symptoms

## Probable Causes

Failure occured when noc-scheduler tried to execute periodic task

## Recommended Actions

Check noc-scheduler, noc-sae and noc-activator logs

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
task | str | {{ yes }} | Task's name

## Alarms

### Raising alarms

`NOC | Periodic | Periodic Failed` events may raise following alarms:

Alarm Class | Description
--- | ---
[NOC \| Periodic \| Periodic Failed](../../../alarm-classes/noc/periodic/periodic-failed.md) | dispose
