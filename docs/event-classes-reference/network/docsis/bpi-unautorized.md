---
uuid: 0cbcf3cf-c124-49c8-9a87-38f3fa20fea3
---
# Network | DOCSIS | BPI Unautorized

Invalid Shared Secret

## Symptoms

## Probable Causes

An unauthorized cable modem has been deleted to enforce BPI authorization for the specified cable modem. The specified cable modem was not performing BPI negotiation.

## Recommended Actions

Check the modem interface configuration for privacy mandatory, or check for errors in the TFTP configuration file.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
mac | mac | {{ yes }} | Cable Modem MAC
sid | int | {{ no }} | Cable Modem SID
interface | interface_name | {{ no }} | Cable interface

## Alarms

### Raising alarms

`Network | DOCSIS | BPI Unautorized` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| DOCSIS \| BPI Unautorized](../../../alarm-classes/network/docsis/bpi-unautorized.md) | dispose
