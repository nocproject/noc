.. _dev-modelinterface-dimensions:

==========================
dimensions Model Interface
==========================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

A measurement of equipment in a particular direction, especially its height, length, or width:

Variables
---------

+---------+--------+---------------------------+----------+----------+---------+
| Name    | Type   | Description               | Required | Constant | Default |
+---------+--------+---------------------------+----------+----------+---------+
|width    | Int    | width in mm               | True     | True     |         |
|         |        |                           |          |          |         |
+---------+--------+---------------------------+----------+----------+---------+
|depth    | Int    | depth in mm               | True     | True     |         |
|         |        |                           |          |          |         |
+---------+--------+---------------------------+----------+----------+---------+
|height   | Int    | height in mm              | True     | True     |         |
|         |        |                           |          |          |         |
+---------+--------+---------------------------+----------+----------+---------+


Examples
--------

::

    "dimensions": {
        "depth": 220,
        "height": 43.6,
        "width": 442
    }