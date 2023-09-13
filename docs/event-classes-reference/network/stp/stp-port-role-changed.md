---
uuid: c614673d-99a0-4901-96ab-ea7b50f36ea2
---
# Network | STP | STP Port Role Changed

STP Port role changed

## Symptoms

possible start of spanning tree rebuilding or interface oper status change

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Interface
role | str | {{ yes }} | Port Role
vlan | int | {{ no }} | VLAN ID
instance | int | {{ no }} | MST instance
