.. _dev-modelinterface-power:

=====================
power Model Interface
=====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Object's power consumption

Variables
---------

+--------------+--------+-----------------------------------------------+------------+------------+-----------+
| Name         | Type   | Description                                   | Required   | Constant   | Default   |
+==============+========+===============================================+============+============+===========+
| power        | float  | Object's own power consumption in W           | True       | True       |           |
+--------------+--------+-----------------------------------------------+------------+------------+-----------+
| is_recursive | bool   | Add nested object's power consumption if true | True       | True       | false     |
+--------------+--------+-----------------------------------------------+------------+------------+-----------+


Examples
--------

::

    "power": {
        "power": 50.0
    }
