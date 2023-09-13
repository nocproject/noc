---
uuid: bcc634b6-6927-49c4-a29c-04cf3b44e4e3
---
# Network | DOCSIS | Invalid CoS

Invalid or unsupported CoS setting

## Symptoms

## Probable Causes

The registration of the specified modem has failed because of an invalid or unsupported CoS setting.

## Recommended Actions

Ensure that the CoS fields in the configuration file are set correctly.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
mac | mac | {{ yes }} | Cable Modem MAC
sid | int | {{ no }} | Cable Modem SID
interface | interface_name | {{ no }} | Cable interface

## Alarms

### Raising alarms

`Network | DOCSIS | Invalid CoS` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| DOCSIS \| Invalid CoS](../../../alarm-classes/network/docsis/invalid-cos.md) | dispose
