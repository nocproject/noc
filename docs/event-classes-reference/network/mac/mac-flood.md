---
uuid: 97f7cbff-e6e6-4e12-86ad-c6caaf46fc1c
---
# Network | MAC | MAC Flood

Flooding MAC Detected

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
mac | mac | {{ yes }} | MAC Address
vlan | int | {{ yes }} | VLAN
interface | interface_name | {{ no }} | Interface

## Alarms

### Raising alarms

`Network | MAC | MAC Flood` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| MAC \| MAC Flood](../../../alarm-classes/network/mac/mac-flood.md) | dispose
