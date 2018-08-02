.. _dev-modelinterface-twinax:

======================
twinax Model Interface
======================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Twinax transceiver (two transceivers connected by cable in the assembly).
Both transceivers have the same serial number and can be inserted in one or two managed object.

Variables
---------

+-------------+--------+--------------------------------------------+------------+------------+-----------+
| Name        | Type   | Description                                | Required   | Constant   | Default   |
+=============+========+============================================+============+============+===========+
| twinax      | bool   | Object is the twinax transceiver           | True       | True       |           |
+-------------+--------+--------------------------------------------+------------+------------+-----------+
| alias       | str    | Virtual connection name for ConnectionRule | True       | True       |           |
+-------------+--------+--------------------------------------------+------------+------------+-----------+
| connection1 | str    | Connection name for first side of twinax   | True       | True       |           |
+-------------+--------+--------------------------------------------+------------+------------+-----------+
| connection2 | str    | Connection name for second side of twinax  | True       | True       |           |
+-------------+--------+--------------------------------------------+------------+------------+-----------+
