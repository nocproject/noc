---
uuid: 7798679b-61e6-40b3-8adb-5d0c5b35de69
---
# Network | DOCSIS | Bad Timing Offset

Bad timing offset detected for Cable Modem

## Symptoms

## Probable Causes

The cable modem is not using the correct starting offset during initial ranging, causing a zero, negative timing offset to be recorded by the CMTS for this modem. The CMTS internal algorithms that rely on the timing offset parameter will not analyze any modems that do not use the correct starting offset. The modems may not be able to function, depending on their physical location on the cable plant.

## Recommended Actions

Locate the cable modem based on the MAC address and report the initial timing offset problem to the cable modem vendor.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
mac | mac | {{ no }} | Cable Modem MAC
sid | int | {{ no }} | Cable Modem SID
offset | str | {{ no }} | Time offset

## Alarms

### Raising alarms

`Network | DOCSIS | Bad Timing Offset` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| DOCSIS \| Bad Timing Offset](../../../alarm-classes/network/docsis/bad-timing-offset.md) | dispose
