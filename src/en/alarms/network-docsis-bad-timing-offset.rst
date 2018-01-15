.. _alarm-class-network-docsis-bad-timing-offset:

====================================
Network | DOCSIS | Bad Timing Offset
====================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
.. todo::
    Describe Network | DOCSIS | Bad Timing Offset symptoms

Probable Causes
---------------
The cable modem is not using the correct starting offset during initial ranging, causing a zero, negative timing offset to be recorded by the CMTS for this modem. The CMTS internal algorithms that rely on the timing offset parameter will not analyze any modems that do not use the correct starting offset. The modems may not be able to function, depending on their physical location on the cable plant.

Recommended Actions
-------------------
Locate the cable modem based on the MAC address and report the initial timing offset problem to the cable modem vendor.

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
mac                  Cable Modem MAC
sid                  Cable Modem SID
offset               Time offset
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-network-docsis-bad-timing-offset`
============= ======================================================================
