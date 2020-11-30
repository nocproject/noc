---
uuid: 62f6386f-ba8d-4f99-b433-4b1d7fb7fd0a
---
# Network | DOCSIS | Invalid Shared Secret

## Symptoms

## Probable Causes

The registration of this modem has failed because of an invalid MIC string.

## Recommended Actions

Ensure that the shared secret that is in the configuration file is the same as the shared secret that is configured in the cable modem.

## Variables

Variable | Description | Default
--- | --- | ---
mac | Cable Modem MAC | {{ no }}
sid | Cable Modem SID | {{ no }}
interface | Cable interface | {{ no }}

## Events

### Opening Events
`Network | DOCSIS | Invalid Shared Secret` may be raised by events

Event Class | Description
--- | ---
[Network \| DOCSIS \| Invalid Shared Secret](../../../event-classes/network/docsis/invalid-shared-secret.md) | dispose
