---
uuid: 3cd44497-6f0e-4a27-b6fe-3ab001681236
---
# NOC | Managed Object | Ping Failed

Failed to ping managed object

## Symptoms

Cannot execute SA tasks on the object

## Probable Causes

The object is not responding to ICMP echo-requests

## Recommended Actions

Check object is alive. Check routing to this object. Check firewalls

## Alarms

### Raising alarms

`NOC | Managed Object | Ping Failed` events may raise following alarms:

Alarm Class | Description
--- | ---
[NOC \| Managed Object \| Ping Failed](../../../alarm-classes/noc/managed-object/ping-failed.md) | dispose
