.. _alarm-class-noc-periodic-periodic-failed:

================================
NOC | Periodic | Periodic Failed
================================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
No specific symptoms

Probable Causes
---------------
Failure occured when noc-scheduler tried to execute periodic task

Recommended Actions
-------------------
Check noc-scheduler, noc-sae and noc-activator logs

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
task                 Task name
==================== ==================================================

Events
------
============= ======================================================================
Opening Event :ref:`event-class-noc-periodic-periodic-failed`
Closing Event :ref:`event-class-noc-periodic-periodic-ok`
============= ======================================================================
