---
uuid: d714bd19-7877-4c6b-8d75-985415d43078
---
# Network | STP | STP Port State Changed

STP Port state changed

## Symptoms

possible start of spanning tree rebuilding or interface oper status change

## Probable Causes

## Recommended Actions

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Interface
state | str | {{ yes }} | Port State
vlan | int | {{ no }} | VLAN ID
instance | int | {{ no }} | MST instance
