==============
Managed Object
==============

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Managed Object is a core concept for NOC. Shortly it is the entity
which can be *managed* by NOC by any means as actively (via CLI, SNMP or HTTP)
or passively (SYSLOG, SNMP Traps, Netflow)

Group Settings
--------------
Group settings for Managed Object are contained in :doc:`/reference/managed-object-profile`

Divisions
---------

Managed Object is participating in several independed *divisions*, each
answering particular question:

* **Administrative:** *Who is responsible for object?*
  See :doc:`/reference/administrative-domain`
* **Network Segment:** *What position in network hierarchy object holds?*
  See :doc:`/reference/network-segment`
* **Container:** *Where object is located?*
  See :doc:`/reference/container`

Managed Object must belong to only one division of particular type

.. todo::
    Complete documentation
