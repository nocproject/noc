.. _dev-modelinterface-plan:

====================
plan Model Interface
====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Arrangement on the plan or on the scheme.
Plan position.

Variables
---------

+---------+--------+-----------------------------------------------------------+------------+------------+-----------+
| Name    | Type   | Description                                               | Required   | Constant   | Default   |
+=========+========+===========================================================+============+============+===========+
| x       | float  | x coordinate, in local units                              | True       | False      |           |
+---------+--------+-----------------------------------------------------------+------------+------------+-----------+
| y       | float  | y coordinate, in local units                              | True       | False      |           |
+---------+--------+-----------------------------------------------------------+------------+------------+-----------+
| bearing | float  | Rotation angle, in degrees, counterclockwise horizontally | False      | False      | 0.0       |
+---------+--------+-----------------------------------------------------------+------------+------------+-----------+
