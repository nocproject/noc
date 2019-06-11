.. _api-datastream-administrativedomain:

===============================
administrativedomain DataStream
===============================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

administrativedomain DataStream contains summarized :ref:`Admninistrative Domain<reference-administrative-domain>`
state

Fields
------

+--------+-----------------+--------------------------------------------------------------------+
| Name   | Type            | Description                                                        |
+========+=================+====================================================================+
| id     | String          | :ref:`Administrative Domain's<reference-administrative-domain>` ID |
+--------+-----------------+--------------------------------------------------------------------+
| name   | String          | Name                                                               |
+--------+-----------------+--------------------------------------------------------------------+
| parent | String          | Parent's ID (if exists)                                            |
+--------+-----------------+--------------------------------------------------------------------+
| tags   | Array of String | List of tags                                                       |
+--------+-----------------+--------------------------------------------------------------------+

Access
------
:ref:`API Key<reference-apikey>` with `datastream:administrativedomain` permissions
required.
