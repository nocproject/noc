---
uuid: 86b92bf2-706e-4900-880d-f1c9c253b206
---
# Network | PIM | Invalid RP

Received Register or Join for invalid RP

## Symptoms

## Probable Causes

A PIM router received a register message from another PIM router that identifies itself as the rendezvous point. If the router is not configured for another rendezvous point, it will not accept the register message.

## Recommended Actions

Configure all leaf routers (first-hop routers to multicast sources) with the IP address of the valid rendezvous point.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
pim_router | ip_address | {{ yes }} | PIM Router IP
invalid_rp | ip_address | {{ yes }} | Invalid RP IP

## Alarms

### Raising alarms

`Network | PIM | Invalid RP` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| PIM \| Invalid RP](../../../alarm-classes/network/pim/invalid-rp.md) | dispose
