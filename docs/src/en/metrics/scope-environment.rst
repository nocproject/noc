.. _metric-scope-environment:

===========
Environment
===========
.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Environment-related metrics

Data Table
----------
ClickHouse Table: `environment`

+----------------+--------------+------------------------------------------------------------+
|Field           |Type          |Description                                                 |
+----------------+--------------+------------------------------------------------------------+
|date            |Date          |Measurement Date                                            |
+----------------+--------------+------------------------------------------------------------+
|ts              |DateTime      |Measurement Timestamp                                       |
+----------------+--------------+------------------------------------------------------------+
|managed_object  |UInt64        |(Key) Reference to sa.ManagedObject model (bi_id)           |
+----------------+--------------+------------------------------------------------------------+
|path            |Array(String) |Path:                                                       |
|                |              |                                                            |
|                |              |* chassis                                                   |
|                |              |* slot                                                      |
|                |              |* module                                                    |
|                |              |* name                                                      |
+----------------+--------------+------------------------------------------------------------+
|elec_current    |Int16         |:ref:`metric-type-environment-electric-current`             |
+----------------+--------------+------------------------------------------------------------+
|sensor_status   |Int8          |:ref:`metric-type-environment-sensor-status`                |
+----------------+--------------+------------------------------------------------------------+
|temperature     |Int16         |:ref:`metric-type-environment-temperature`                  |
+----------------+--------------+------------------------------------------------------------+
|voltage         |Float32       |:ref:`metric-type-environment-voltage`                      |
+----------------+--------------+------------------------------------------------------------+
