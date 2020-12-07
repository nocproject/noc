---
uuid: 1679a32f-74cb-4567-af15-65e817df02c7
---
# Network | DOCSIS | Max CPE Reached

Maximum number of CPE reached

## Symptoms

## Probable Causes

The maximum number of devices that can be attached to the cable modem has been exceeded. Therefore, the device with the specified IP address will not be added to the modem with the specified SID.

## Recommended Actions

Locate the specified device and place the device on a different cable modem with another SID.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
mac | mac | {{ no }} | CPE MAC
ip | ip_address | {{ no }} | CPE IP
modem_mac | mac | {{ no }} | Cable Modem MAC
sid | int | {{ no }} | Cable Modem SID
interface | interface_name | {{ no }} | Cable interface

## Alarms

### Raising alarms

`Network | DOCSIS | Max CPE Reached` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| DOCSIS \| Max CPE Reached](../../../alarm-classes/network/docsis/max-cpe-reached.md) | dispose
