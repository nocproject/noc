---
uuid: 4b308283-0654-4568-99ff-07f4c4ef37e8
---
# Network | PIM | MSDP Peer Down

## Symptoms

Multicast flows lost

## Probable Causes

Link failure or protocol misconfiguration

## Recommended Actions

Check links and local and neighbor router configuration

## Variables

Variable | Description | Default
--- | --- | ---
peer | Peer's IP | {{ no }}
vrf | VRF | {{ no }}
reason | Reason | {{ no }}

## Events

### Opening Events
`Network | PIM | MSDP Peer Down` may be raised by events

Event Class | Description
--- | ---
[Network \| PIM \| MSDP Peer Down](../../../event-classes/network/pim/msdp-peer-down.md) | dispose

### Closing Events
`Network | PIM | MSDP Peer Down` may be cleared by events

Event Class | Description
--- | ---
[Network \| PIM \| MSDP Peer Up](../../../event-classes/network/pim/msdp-peer-up.md) | dispose
