---
uuid: 913a40f4-b51a-42c5-b490-ad03f4b7edd7
---
# NOC | IPAM | VRF Group Address Collision

VRF Group address collision detected

## Symptoms

## Probable Causes

Equipment misconfiguration of IP address misallocation

## Recommended Actions

Check address allocation and equipment configuration

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
address | str | {{ yes }} | Address
vrf | str | {{ yes }} | VRF
interface | str | {{ no }} | Interface
existing_vrf | str | {{ yes }} | Existing VRF
existing_object | str | {{ no }} | Existing Object

## Alarms

### Raising alarms

`NOC | IPAM | VRF Group Address Collision` events may raise following alarms:

Alarm Class | Description
--- | ---
[NOC \| IPAM \| VRF Group Address Collision](../../../alarm-classes/noc/ipam/vrf-group-address-collision.md) | dispose
