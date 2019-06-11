.. _alarm-class-vendor-cisco-scos-security-attack-attack-detected:

===========================================================
Vendor | Cisco | SCOS | Security | Attack | Attack Detected
===========================================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Possible DoS/DDoS traffic from source

Probable Causes
---------------
Virus/Botnet activity or malicious actions

Recommended Actions
-------------------
Negotiate the source if it is your customer, or ignore

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
from_ip              From IP
to_ip                To IP
from_side            From Side
proto                Protocol
open_flows           Open Flows
suspected_flows      Suspected Flows
action               Action
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-vendor-cisco-scos-security-attack-attack-detected`
Closing Event :ref:`event-class-vendor-cisco-scos-security-attack-end-of-attack-detected`
============= ======================================================================
