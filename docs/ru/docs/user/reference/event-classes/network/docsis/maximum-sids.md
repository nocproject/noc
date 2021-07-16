---
uuid: c3c26486-18bf-4296-b621-fd10c3f63070
---
# Network | DOCSIS | Maximum SIDs

The maximum number of SIDs has been allocated

## Symptoms

## Probable Causes

The maximum number of SIDs has been allocated to the specified line card.

## Recommended Actions

Assign the cable modem to another line card.

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
interface | interface_name | {{ yes }} | Cable interface

## Alarms

### Raising alarms

`Network | DOCSIS | Maximum SIDs` events may raise following alarms:

Alarm Class | Description
--- | ---
[Network \| DOCSIS \| Maximum SIDs](../../../alarm-classes/network/docsis/maximum-sids.md) | dispose
