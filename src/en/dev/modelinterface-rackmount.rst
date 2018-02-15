.. _dev-modelinterface-rackmount:

=========================
rackmount Model Interface
=========================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Rack mounted equipment.
Used to store position in rack.


Variables
---------

+----------+--------+--------------------------------------------------+------------+------------+-----------+
| Name     | Type   | Description                                      | Required   | Constant   | Default   |
+==========+========+==================================================+============+============+===========+
| units    | float  | Size in units                                    | True       | True       |           |
+----------+--------+--------------------------------------------------+------------+------------+-----------+
| position | int    | Bottom rack position (in units)                  | False      | False      |           |
+----------+--------+--------------------------------------------------+------------+------------+-----------+
| side     | str    | Mounting side (f/r)                              | False      | False      |           |
|          |        |                                                  |            |            |           |
|          |        | f - mounted at the front side                    |            |            |           |
|          |        | r - mounted at the rear side                     |            |            |           |
+----------+--------+--------------------------------------------------+------------+------------+-----------+
| shift    | int    | Shift 0/1/2 holes up                             | False      | False      |           |
|          |        |                                                  |            |            |           |
|          |        | 0 - fit to the unit                              |            |            |           |
|          |        | 1 - displacement 1 hole up relative to the unit  |            |            |           |
|          |        | 2 - displacement 2 holes up relative to the unit |            |            |           |
+----------+--------+--------------------------------------------------+------------+------------+-----------+


Examples
--------

::

        "rackmount": {
            "units": 1.0
        }
