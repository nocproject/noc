---
uuid: bb0a5d88-8970-4a54-826c-7d750afd10c6
---
# Network | PIM | Neighbor Down

PIM Neighbor down

## Symptoms

Multicast flows lost

## Probable Causes

PIM protocol configuration problem or link failure

## Recommended Actions

Check links and local and neighbor's router configuration

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Interface
neighbor | ip_address | {{ yes }} | Neighbor's IP
vrf | str | {{ no }} | VRF
reason | str | {{ no }} | Reason

## Alarms

### Raising alarms

`Network | PIM | Neighbor Down` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| PIM \| Neighbor Down](../../../alarm-classes/network/pim/neighbor-down.md) | dispose
