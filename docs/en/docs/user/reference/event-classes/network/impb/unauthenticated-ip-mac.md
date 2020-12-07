---
uuid: 9ef43611-4a64-4e61-9e96-dd0f4cc8caa1
---
# Network | IMPB | Unauthenticated IP-MAC

Unauthenticated IP-MAC

## Symptoms

Discard user connection attempts

## Probable Causes

## Recommended Actions

Check user IP and MAC, check IMPB entry, check topology

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
ip | ip_address | {{ yes }} | User IP
mac | mac | {{ yes }} | User MAC
interface | interface_name | {{ yes }} | Affected interface

## Alarms

### Raising alarms

`Network | IMPB | Unauthenticated IP-MAC` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| IMPB \| Unauthenticated IP-MAC](../../../alarm-classes/network/impb/unauthenticated-ip-mac.md) | dispose
