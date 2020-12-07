---
uuid: 5109bea9-c7da-4132-98b5-35f1767d4421
---
# Network | MSDP | Peer Down

## Symptoms

## Probable Causes

## Recommended Actions

Check msdp peer aviability, check msdp peer configuration changes

## Variables

Variable | Description | Default
--- | --- | ---
peer | Peer's IP | {{ no }}
vrf | VRF | {{ no }}
reason | Reason | {{ no }}

## Events

### Opening Events
`Network | MSDP | Peer Down` may be raised by events

Event Class | Description
--- | ---
[Network \| MSDP \| Peer Down](../../../event-classes/network/msdp/peer-down.md) | dispose

### Closing Events
`Network | MSDP | Peer Down` may be cleared by events

Event Class | Description
--- | ---
[Network \| MSDP \| Peer Up](../../../event-classes/network/msdp/peer-up.md) | dispose
