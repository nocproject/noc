---
uuid: c7ecc87a-070b-469a-9434-ffe3e924a76b
---
# Network | MAC | Duplicate MAC

## Symptoms

## Probable Causes

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
mac | MAC Address | {{ no }}
one_interface | First interface | {{ no }}
two_interface | Second interface | {{ no }}
one_description | Interface description | `=oneInterfaceDS.description`
two_description | Interface description | `=twoInterfaceDS.description`

## Events

### Opening Events
`Network | MAC | Duplicate MAC` may be raised by events

Event Class | Description
--- | ---
[Network \| MAC \| Duplicate MAC](../../../event-classes/network/mac/duplicate-mac.md) | dispose
