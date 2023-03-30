---
uuid: fa9cc838-9ec4-4080-907a-13390b5b1285
---
# Network | MAC | MAC Flap

MAC Flap detected

## Symptoms

## Probable Causes

The system found the specified host moving between the specified ports.

## Recommended Actions

Examine the network for possible loops.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
mac | mac | {{ yes }} | MAC Address
vlan | int | {{ yes }} | VLAN
from_interface | interface_name | {{ yes }} | From interface
to_interface | interface_name | {{ yes }} | To interface

## Alarms

### Raising alarms

`Network | MAC | MAC Flap` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| MAC \| MAC Flap](../../../alarm-classes/network/mac/mac-flap.md) | dispose
