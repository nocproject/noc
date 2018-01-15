.. _alarm-class-noc-pm-high-warning:

=======================
NOC | PM | High Warning
=======================
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Symptoms
--------
Values are out of second threshold value.

Probable Causes
---------------
Metric value cross critical threshold

Recommended Actions
-------------------
.. todo::
    Describe NOC | PM | High Warning recommended actions

Variables
----------
==================== ==================================================
Name                 Description
==================== ==================================================
metric               Metric name
scope                Metric scope
path                 Path to component raising alarm
value                Metric value
threshold            Threshold value
window_type          Type of window (time or count)
window               Window size
window_function      Function apply to window
==================== ==================================================
