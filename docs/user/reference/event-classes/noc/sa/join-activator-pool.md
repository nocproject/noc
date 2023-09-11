---
uuid: 2aaf7e96-8221-44e0-bc49-aa82b3bb20bd
---
# NOC | SA | Join Activator Pool

## Symptoms

SA performance increased

## Probable Causes

noc-activator process been launched

## Recommended Actions

No recommended actions

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

`NOC | SA | Join Activator Pool` events may raise following alarms:

Alarm Class | Description
--- | ---
[NOC \| SA \| Activator Pool Degraded](../../../alarm-classes/noc/sa/activator-pool-degraded.md) | raise

### Clearing alarms

`NOC | SA | Join Activator Pool` events may clear following alarms:

Alarm Class | Description
--- | ---
[NOC \| SA \| Activator Pool Degraded](../../../alarm-classes/noc/sa/activator-pool-degraded.md) | clear
