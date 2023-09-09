---
uuid: 3fe3f173-f7e5-44bb-89fc-7d9bf81ea22d
---
# Network | DOCSIS | Maximum Capacity Reached

Current total reservation exceeds maximum configured reservation

## Symptoms

## Probable Causes

The currently reserved capacity on the upstream channel already exceeds its virtual reservation capacity, based on the configured subscription level limit. Increasing the subscription level limit on the current upstream channel will place you at risk of being unable to guarantee the individual reserved rates for modems since this upstream channel is already oversubscribed.

## Recommended Actions

Load-balance the modems that are requesting the reserved upstream rate on another upstream channel.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Cable interface
upstream | str | {{ no }} | Upstream
cur_bps | int | {{ no }} | Current bps reservation
res_bps | int | {{ no }} | Reserved bps

## Alarms

### Raising alarms

`Network | DOCSIS | Maximum Capacity Reached` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| DOCSIS \| Maximum Capacity Reached](../../../alarm-classes/network/docsis/maximum-capacity-reached.md) | dispose
