---
uuid: 65556dfa-77c5-4840-9306-30dd8d3d0164
---
# Network | BGP | Max Prefixes Warning

Max prefixes warning

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
