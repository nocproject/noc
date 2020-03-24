.. _api-datastream-cfgping:

==================
cfgping DataStream
==================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

`cfgping` datastream contains configuration
for :ref:`ping<services-ping>` service

Fields
------

+-----------------+-----------------+--------------------------------------------------------------------------------+
| Name            | Type            | Description                                                                    |
+=================+=================+================================================================================+
| id              | String          | :ref:`Managed Object's<reference-managed-object>` id                           |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| change_id       | String          | :ref:`Record's change id<api-datastream-changeid>`                             |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| pool            | String          | :ref:`Pool's name<reference-pool>`                                             |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| fm_pool         | String          | :ref:`Pool's name<reference-pool>` for FM event processing                     |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| interval        | Integer         | Probing rounds interval in seconds                                             |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| policy          | String          | Probing policy:                                                                |
|                 |                 |                                                                                |
|                 |                 | * f - Success on first successful try                                          |
|                 |                 | * a - Success only if all tries successful                                     |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| size            | Integer         | ICMP Echo-Request packet size                                                  |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| count           | Integer         | Probe attempts per round                                                       |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| timeout         | Integer         | Probe timeout in seconds                                                       |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| report_rtt      | Boolean         | Report :ref:`Ping | RTT<metric-type-ping-rtt>` metric per each round           |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| report_attempts | Boolean         | Report :ref:`Ping | Attempts<metric-type-ping-attempts>` metric per each round |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| status          | Null            | Reserved                                                                       |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| name            | String          | :ref:`Managed Object's<reference-managed-object>` name                         |
+-----------------+-----------------+--------------------------------------------------------------------------------+
| bi_id           | Integer         | :ref:`Managed Object's<reference-managed-object>` BI Id                        |
+-----------------+-----------------+--------------------------------------------------------------------------------+

:todo:
    Add BI ID reference

Filters
-------

.. function:: pool(name)

    Restrict stream to objects belonging to pool `name`

    :param name: Pool name

Access
------
:ref:`API Key<reference-apikey>` with `datastream:cfgping` permissions
required.
