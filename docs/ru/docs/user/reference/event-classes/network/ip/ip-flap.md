---
uuid: 16efc0f6-d3f0-4527-850c-e783b1287926
---
# Network | IP | IP Flap

IP Flapped between interfaces

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
ip | ip_address | {{ yes }} | Flapped IP
mac | mac | {{ no }} | MAC
from_interface | interface_name | {{ yes }} | From interface
to_interface | interface_name | {{ yes }} | To interface

## Alarms

### Raising alarms

`Network | IP | IP Flap` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| IP \| IP Flap](../../../alarm-classes/network/ip/ip-flap.md) | dispose
