---
uuid: 7cec091a-aceb-4c37-8455-4ab32e9cd79a
---
# Network | DOCSIS | Bad Timing Offset

## Symptoms

## Probable Causes

The cable modem is not using the correct starting offset during initial ranging, causing a zero, negative timing offset to be recorded by the CMTS for this modem. The CMTS internal algorithms that rely on the timing offset parameter will not analyze any modems that do not use the correct starting offset. The modems may not be able to function, depending on their physical location on the cable plant.

## Recommended Actions

Locate the cable modem based on the MAC address and report the initial timing offset problem to the cable modem vendor.

## Variables

Variable | Description | Default
--- | --- | ---
mac | Cable Modem MAC | {{ no }}
sid | Cable Modem SID | {{ no }}
offset | Time offset | {{ no }}

## Events

### Opening Events
`Network | DOCSIS | Bad Timing Offset` may be raised by events

Event Class | Description
--- | ---
[Network \| DOCSIS \| Bad Timing Offset](../../../event-classes/network/docsis/bad-timing-offset.md) | dispose
