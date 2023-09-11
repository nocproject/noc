---
uuid: 68746449-10e4-44f6-9c81-66569fc22e78
---
# Network | DOCSIS | Invalid QoS

## Symptoms

## Probable Causes

The registration of the specified modem has failed because of an invalid or unsupported QoS setting.

## Recommended Actions

Ensure that the QoS fields in the configuration file are set correctly.

## Variables

Variable | Description | Default
--- | --- | ---
mac | Cable Modem MAC | {{ no }}
sid | Cable Modem SID | {{ no }}
interface | Cable interface | {{ no }}

## Events

### Opening Events
`Network | DOCSIS | Invalid QoS` may be raised by events

Event Class | Description
--- | ---
[Network \| DOCSIS \| Invalid QoS](../../../event-classes/network/docsis/invalid-qos.md) | dispose
