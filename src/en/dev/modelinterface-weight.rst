.. _dev-modelinterface-weight:

======================
weight Model Interface
======================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Object's weight properties

+-------------+--------+--------------------------------------------+------------+------------+-----------+
| Name        | Type   | Description                                | Required   | Constant   | Default   |
+=============+========+============================================+============+============+===========+
|weight       | Float  | Own weight of object in kg                 |  True      |   True     |           |
+-------------+--------+--------------------------------------------+------------+------------+-----------+
|is_recursive | Bool   | true - add to the weight of the object     |            |            |           |
|             |        | the weight of its modules (connected to    |  True      |   True     |  False    |
|             |        | connection direction i                     |            |            |           |
+-------------+--------+--------------------------------------------+------------+------------+-----------+