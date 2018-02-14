.. _dev-modelinterface-pop:

===================
pop Model Interface
===================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Point of present

Variables
---------

+--------+--------+---------------+------------+------------+-----------+
| Name   | Type   | Description   | Required   | Constant   | Default   |
+========+========+===============+============+============+===========+
| level  | int    | PoP level     | True       | True       |           |
+--------+--------+---------------+------------+------------+-----------+

Levels of PoP:

+---------------+---------+---------------------------------+
| Type          |   Level | Description                     |
+===============+=========+=================================+
| International |      70 | International points of present |
+---------------+---------+---------------------------------+
| National      |      60 | National points of present      |
+---------------+---------+---------------------------------+
| Regional      |      50 | Regional points of present      |
+---------------+---------+---------------------------------+
| Core          |      40 | Metro Core                      |
+---------------+---------+---------------------------------+
| Agregation    |      30 | Agregation nodes                |
+---------------+---------+---------------------------------+
| Access        |      20 | Access nodes                    |
+---------------+---------+---------------------------------+
| Client        |      10 | Customer premises               |
+---------------+---------+---------------------------------+

Examples
--------

::

    "pop": {
        "level": 50
    }
