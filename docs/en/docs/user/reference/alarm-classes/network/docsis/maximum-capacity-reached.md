---
uuid: b1fea1e4-8b4c-4116-af4d-850ce41a79fe
---
# Network | DOCSIS | Maximum Capacity Reached

## Symptoms

## Probable Causes

The currently reserved capacity on the upstream channel already exceeds its virtual reservation capacity, based on the configured subscription level limit. Increasing the subscription level limit on the current upstream channel will place you at risk of being unable to guarantee the individual reserved rates for modems since this upstream channel is already oversubscribed.

## Recommended Actions

Load-balance the modems that are requesting the reserved upstream rate on another upstream channel.

## Variables

Variable | Description | Default
--- | --- | ---
interface | Cable interface | {{ no }}
upstream | Upstream | {{ no }}
cur_bps | Current bps reservation | {{ no }}
res_bps | Reserved bps | {{ no }}

## Events

### Opening Events
`Network | DOCSIS | Maximum Capacity Reached` may be raised by events

Event Class | Description
--- | ---
[Network \| DOCSIS \| Maximum Capacity Reached](../../../event-classes/network/docsis/maximum-capacity-reached.md) | dispose
