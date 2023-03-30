---
uuid: c0d11fbc-06e7-426e-8d69-b24f5b1fe249
---
# Network | LLDP | Remote Tables Change

LLDP Remote Tables Change

## Symptoms

Possible instability of network connectivity

## Probable Causes

A lldpRemTablesChange notification is sent when the value of lldpStatsRemTableLastChangeTime changes.
It can beutilized by an NMS to trigger LLDP remote systems table maintenance polls.
Note that transmission of lldpRemTablesChange notifications are throttled by the agent, as specified by the 'lldpNotificationInterval' object

## Recommended Actions

Large amount of deletes may indicate instable link

## Variables

Variable | Type | Required | Description
--- | --- | --- | ---
table_inserts | int | {{ yes }} | Number of insers per interval
table_deletes | int | {{ yes }} | Number of deletes per interval
table_drops | int | {{ yes }} | Number of drops per interval
table_ageouts | int | {{ yes }} | Number of aged entries per interval
