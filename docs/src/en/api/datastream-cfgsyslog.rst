.. _api-datastream-cfgsyslog:

====================
cfgsyslog DataStream
====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

`cfgsyslog` datastream contains configuration
for :ref:`syslogcollector<services-syslogcollector>` service

Fields
------

+-----------+-----------------+------------------------------------------------------------+
| Name      | Type            | Description                                                |
+===========+=================+============================================================+
| id        | String          | :ref:`Managed Object's<reference-managed-object>` id       |
+-----------+-----------------+------------------------------------------------------------+
| change_id | String          | :ref:`Record's change id<api-datastream-changeid>`         |
+-----------+-----------------+------------------------------------------------------------+
| pool      | String          | :ref:`Pool's name<reference-pool>`                         |
+-----------+-----------------+------------------------------------------------------------+
| fm_pool   | String          | :ref:`Pool's name<reference-pool>` for FM event processing |
+-----------+-----------------+------------------------------------------------------------+
| addresses | Array of String | List of syslog sources' IP addresses                       |
+-----------+-----------------+------------------------------------------------------------+

Filters
-------

.. function:: pool(name)

    Restrict stream to objects belonging to pool `name`

    :param name: Pool name

Access
------
:ref:`API Key<reference-apikey>` with `datastream:cfgsyslog` permissions
required.
