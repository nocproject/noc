.. _api-datastream-resourcegroup:

========================
resourcegroup DataStream
========================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

*resourcegroup* DataStream contains summarized :ref:`Resource Group<reference-resource-group>`
state

Fields
------

+---------------+--------+---------------------------------------------------------------------+
| Name          | Type   | Description                                                         |
+===============+========+=====================================================================+
| id            | String | :ref:`Administrative Domain's<reference-administrative-domain>` ID  |
+---------------+--------+---------------------------------------------------------------------+
| name          | String | Name                                                                |
+---------------+--------+---------------------------------------------------------------------+
| parent        | String | Parent's ID (if exists)                                             |
+---------------+--------+---------------------------------------------------------------------+
| technology    | Object | Resource Group's :ref:`Technology<reference-technology>`            |
+---------------+--------+---------------------------------------------------------------------+
| remote_system | Object | Source :ref:`remote system<reference-remote-system>` for object     |
+---------------+--------+---------------------------------------------------------------------+
| * id          | String | External system's id                                                |
+---------------+--------+---------------------------------------------------------------------+
| * name        | String | External system's name                                              |
+---------------+--------+---------------------------------------------------------------------+
| remote_id     | String | External system's id (Opaque attribbute)                            |
+---------------+--------+---------------------------------------------------------------------+

Access
------
:ref:`API Key<reference-apikey>` with `datastream:resourcegroup` permissions
required.
