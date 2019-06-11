.. _event-class-network-lldp-remote-tables-change:

=====================================
Network | LLDP | Remote Tables Change
=====================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

LLDP Remote Tables Change

Symptoms
--------
Possible instability of network connectivity

Probable Causes
---------------
A lldpRemTablesChange notification is sent when the value of lldpStatsRemTableLastChangeTime changes.
It can beutilized by an NMS to trigger LLDP remote systems table maintenance polls.
Note that transmission of lldpRemTablesChange notifications are throttled by the agent, as specified by the 'lldpNotificationInterval' object

Recommended Actions
-------------------
Large amount of deletes may indicate instable link

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
table_inserts        Number of insers per interval
table_deletes        Number of deletes per interval
table_drops          Number of drops per interval
table_ageouts        Number of aged entries per interval
==================== ==================================================
