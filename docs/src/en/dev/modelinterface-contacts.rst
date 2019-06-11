.. _dev-modelinterface-contacts:

========================
contacts Model Interface
========================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Administrative, billing and technical contacts for container
(PoP, Room, Rack)

Variables
---------

+------------------+---------+-------------------------------+----------+----------+---------+
| Name             | Type    | Description                   | Required | Constant | Default |
+------------------+---------+-------------------------------+----------+----------+---------+
| has_contacts     | Boolean | Object can hold               | Yes      | Yes      | true    |
|                  |         | contact information           |          |          |         |
+------------------+---------+-------------------------------+----------+----------+---------+
| administrative   | String  | Administrative contacts       | No       | No       |         |
|                  |         | including access and passes   |          |          |         |
+------------------+---------+-------------------------------+----------+----------+---------+
| billing          | String  | Billing contacts, including   | No       | No       |         |
|                  |         | agreement negotiations,       |          |          |         |
|                  |         | bills and payments            |          |          |         |
+------------------+---------+-------------------------------+----------+----------+---------+
| technical        | String  | Technical contacts,           | No       | No       |         |
|                  |         | including on-site engineering |          |          |         |
+------------------+---------+-------------------------------+----------+----------+---------+

Examples
--------

::

    "contacts": {
        "has_contacts": "true"
    }
