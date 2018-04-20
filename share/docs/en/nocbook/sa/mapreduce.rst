Map/Reduce Tasks
****************
Overview
========
Map/Reduce tasks is a way of parallel execution of scripts on large number of equipment with final validation
and processing of the result.

Map/Reduce tasks are combined from the three entries: Object Selectors, Map Scripts and Reduce Scripts

Object Selectors
================
Object selectors are like preserved queries returning a list of managed objects. Object selector can filter managed objects using
given criteria. Object selectors can use result of other selectors, allowing to combine them together to reach any required granularity.

The task of the object selector is to determine on which managed objects to execute Map Scripts.

For example:

* All objects
* All Cisco IOS-based
* All Cisco MPLS PE
* All access switches
* Access switches in Area A
* Access switches in Area B
* Access switches in areas A and B

Map Scripts
===========
Map Scripts are the common Service Activation scripts which are executed in parallel on all managed objects determined by selector.
The results of Map Scripts are returned to the Reduce Script. Some Map Scripts can fail, Some may not be executed at all. This is
normal situation. This is a task of Reduce script to process failure condition properly.

Reduce Scripts
==============
Reduce Scripts are to process the results of all Map Scripts at once. The common result of Reduce Script is an report, though
it is possible even to start a new Map/Reduce task.
