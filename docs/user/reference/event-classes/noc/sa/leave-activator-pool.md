---
uuid: 49b06b2f-4060-4a34-9b85-e34a9f425889
---
# NOC | SA | Leave Activator Pool

## Symptoms

SA performance decreased

## Probable Causes

noc-activator process been stopped

## Recommended Actions

Check appropriative process

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
name | str | {{ yes }} | Activator pool name
instance | str | {{ yes }} | Activator instance
sessions | int | {{ yes }} | Instance's script sessions
min_members | int | {{ yes }} | Pool's members lower threshold
min_sessions | int | {{ yes }} | Pool's sessions lower threshold
pool_members | int | {{ yes }} | Pool's current members
pool_sessions | int | {{ yes }} | Pool's current sessions limit

## Alarms

### Raising alarms

`NOC | SA | Leave Activator Pool` events may raise following alarms:

Alarm Class | Description
--- | ---
[NOC \| SA \| Activator Pool Degraded](../../../alarm-classes/noc/sa/activator-pool-degraded.md) | raise

### Clearing alarms

`NOC | SA | Leave Activator Pool` events may clear following alarms:

Alarm Class | Description
--- | ---
[NOC \| SA \| Activator Pool Degraded](../../../alarm-classes/noc/sa/activator-pool-degraded.md) | clear
