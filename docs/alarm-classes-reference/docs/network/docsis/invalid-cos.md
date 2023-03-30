---
uuid: 17ace2e2-4516-4142-81aa-6a2c8462d5af
---
# Network | DOCSIS | Invalid CoS

## Symptoms

## Probable Causes

The registration of the specified modem has failed because of an invalid or unsupported CoS setting.

## Recommended Actions

Ensure that the CoS fields in the configuration file are set correctly.

## Variables

Variable | Description | Default
--- | --- | ---
mac | Cable Modem MAC | {{ no }}
sid | Cable Modem SID | {{ no }}
interface | Cable interface | {{ no }}

## Events

### Opening Events
`Network | DOCSIS | Invalid CoS` may be raised by events

Event Class | Description
--- | ---
[Network \| DOCSIS \| Invalid CoS](../../../event-classes/network/docsis/invalid-cos.md) | dispose
