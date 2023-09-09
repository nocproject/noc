---
uuid: c7b07703-98e0-42e7-b43e-afdfd3492cef
---
# Network | IP | ARP Moved

ARP Moved

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ no }} | BFD interface
ip | ip_address | {{ yes }} | IP
from_mac | mac | {{ yes }} | From MAC
to_mac | mac | {{ yes }} | To MAC

## Alarms

### Raising alarms

`Network | IP | ARP Moved` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| IP \| ARP Moved](../../../alarm-classes/network/ip/arp-moved.md) | dispose
