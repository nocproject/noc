---
uuid: 468a5649-f050-44ad-88cc-aa55e616207e
---
# Network | BGP | Max Prefixes Exceeds

Max prefixes exceeds

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
peer | ip_address | {{ yes }} | Peer
vrf | str | {{ no }} | VRF
as | int | {{ no }} | Peer AS
recv | int | {{ yes }} | Prefixes recieved
max | int | {{ no }} | Maximum prefixes
