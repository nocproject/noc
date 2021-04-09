---
uuid: 5a225d20-256c-4bb6-8504-0562d0b2a2d4
---
# Chassis | CPU | CPU Exhausted

## Symptoms

Device not responce, can not establish new connections

## Probable Causes

High CPU utilization

## Recommended Actions

Lower storm detect threshold, filter waste traffic on connected devices, restrict SNMP Views

## Events

### Opening Events
`Chassis | CPU | CPU Exhausted` may be raised by events

Event Class | Description
--- | ---
[Vendor \| DLink \| DxS \| Chassis \| CPU \| Safeguard Engine enters EXHAUSTED mode](../../../event-classes/vendor/dlink/dxs/chassis/cpu/safeguard-engine-enters-exhausted-mode.md) | dispose

### Closing Events
`Chassis | CPU | CPU Exhausted` may be cleared by events

Event Class | Description
--- | ---
[Vendor \| DLink \| DxS \| Chassis \| CPU \| Safeguard Engine enters NORMAL mode](../../../event-classes/vendor/dlink/dxs/chassis/cpu/safeguard-engine-enters-normal-mode.md) | dispose
