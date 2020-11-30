---
uuid: 099d5271-1581-4059-9872-b8b98621e529
---
# NOC | IPAM | VRF Group Address Collision

## Symptoms

## Probable Causes

Equipment misconfiguration of IP address misallocation

## Recommended Actions

Check address allocation and equipment configuration

## Variables

Variable | Description | Default
--- | --- | ---
address | Address | {{ no }}
vrf | VRF | {{ no }}
interface | Interface | {{ no }}
existing_vrf | Existing VRF | {{ no }}
existing_object | Existing Object | {{ no }}

## Events

### Opening Events
`NOC | IPAM | VRF Group Address Collision` may be raised by events

Event Class | Description
--- | ---
[NOC \| IPAM \| VRF Group Address Collision](../../../event-classes/noc/ipam/vrf-group-address-collision.md) | dispose
