---
uuid: 7e3511aa-2e12-4c02-b05e-98920ea86604
---
# Vendor | DLink | DxS | Chassis | CPU | Safeguard Engine enters EXHAUSTED mode

Safeguard Engine enters EXHAUSTED mode

## Symptoms

Device not responce, can not establish new connections

## Probable Causes

High CPU utilization

## Recommended Actions

Lower storm detect threshold, filter waste traffic on connected devices, restrict SNMP Views

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
unit | int | {{ no }} | Unit number in stack

## Alarms

### Raising alarms

`Vendor | DLink | DxS | Chassis | CPU | Safeguard Engine enters EXHAUSTED mode` events may raise following alarms:

Alarm Class | Description
--- | ---
[Chassis \| CPU \| CPU Exhausted](../../../../../../alarm-classes/chassis/cpu/cpu-exhausted.md) | dispose
