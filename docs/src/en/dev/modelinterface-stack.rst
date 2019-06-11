.. _dev-modelinterface-stack:

=====================
stack Model Interface
=====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Indication of stack/virtual chassis/cluster

Variables
---------

+-----------+--------+-----------------------+------------+-------------+-----------+
| Name      | Type   | Description           | Required   | Conastant   | Default   |
+===========+========+=======================+============+=============+===========+
| stackable | bool   | Object can be stacked | False      | True        |           |
+-----------+--------+-----------------------+------------+-------------+-----------+
| member    | str    | Stack member id       | False      | False       |           |
+-----------+--------+-----------------------+------------+-------------+-----------+

Examples
--------

::

    "stack": {
        "stackable": true
    }
