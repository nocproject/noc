---
uuid: dbd74264-b2fd-4a35-b858-79859fcb0bee
---
# Network | DOCSIS | Invalid Shared Secret

Invalid Shared Secret

## Symptoms

## Probable Causes

The registration of this modem has failed because of an invalid MIC string.

## Recommended Actions

Ensure that the shared secret that is in the configuration file is the same as the shared secret that is configured in the cable modem.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
mac | mac | {{ yes }} | Cable Modem MAC
sid | int | {{ no }} | Cable Modem SID
interface | interface_name | {{ no }} | Cable interface

## Alarms

### Raising alarms

`Network | DOCSIS | Invalid Shared Secret` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| DOCSIS \| Invalid Shared Secret](../../../alarm-classes/network/docsis/invalid-shared-secret.md) | dispose
