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

Power consumption may be exact (is_recursive = false), when power represents total power consumption,
or recursive (is_recursive = true), when total power is a sum of power and a power consumption of all nested elements

Examples
--------

::

    "power": {
        "power": 50.0
    }
