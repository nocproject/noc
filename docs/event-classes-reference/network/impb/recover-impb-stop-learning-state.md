---
uuid: 3f84402f-4968-439b-902b-1d1b1519aa78
---
# Network | IMPB | Recover IMPB stop learning state

Port 28 recovers from IMPB stop learning state

## Symptoms

Restore ability for incoming connections

## Probable Causes

## Recommended Actions

Check IMPB entry, check topology

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Affected interface

## Alarms

### Clearing alarms

`Network | IMPB | Recover IMPB stop learning state` events may clear following alarms:

Alarm Class | Description
--- | ---
[Network \| IMPB \| Unauthenticated IP-MAC](../../../alarm-classes/network/impb/unauthenticated-ip-mac.md) | dispose
