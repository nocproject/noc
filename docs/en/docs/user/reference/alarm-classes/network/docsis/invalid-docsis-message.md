---
uuid: c3b73a9c-e6ed-47fa-a970-5765584339c2
---
# Network | DOCSIS | Invalid DOCSIS Message

## Symptoms

## Probable Causes

A cable modem that is not DOCSIS-compliant has attempted to send an invalid DOCSIS message.

## Recommended Actions

Locate the cable modem that sent this message and replace it with DOCSIS-compliant modem.

## Variables

Variable | Description | Default
--- | --- | ---
interface | Cable interface | {{ no }}
mac | Cable Modem MAC | {{ no }}
sid | Cable Modem SID | {{ no }}

## Events

### Opening Events
`Network | DOCSIS | Invalid DOCSIS Message` may be raised by events

Event Class | Description
--- | ---
[Network \| DOCSIS \| Invalid DOCSIS Message](../../../event-classes/network/docsis/invalid-docsis-message.md) | dispose
