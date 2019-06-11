.. _dev-modelinterface-rack:

====================
rack Model Interface
====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Rack enclosures

Variables
---------

+------------+--------+-------------------------------------------+------------+------------+-----------+
| Name       | Type   | Description                               | Required   | Constant   | Default   |
+============+========+===========================================+============+============+===========+
| units      | int    | Internal height in units                  | True       | True       |           |
+------------+--------+-------------------------------------------+------------+------------+-----------+
| width      | int    | Max. equipment width in mm                | True       | True       |           |
+------------+--------+-------------------------------------------+------------+------------+-----------+
| depth      | int    | Max. equipment depth in mm                | True       | True       |           |
+------------+--------+-------------------------------------------+------------+------------+-----------+
| front_door | str    | Front door configuration                  | True       | True       |           |
|            |        |                                           |            |            |           |
|            |        |  o - open, hasn't door                    |            |            |           |
|            |        |  c - closed, blank door                   |            |            |           |
|            |        |  l - one section, opens on the left side  |            |            |           |
|            |        |  r - one section, opens on the right side |            |            |           |
|            |        |  2 - two sections                         |            |            |           |
+------------+--------+-------------------------------------------+------------+------------+-----------+
| rear_door  | str    | Rear door configuration                   | True       | True       |           |
|            |        |                                           |            |            |           |
|            |        |  o - open, hasn't door                    |            |            |           |
|            |        |  c - closed, blank door                   |            |            |           |
|            |        |  l - one section, opens on the left side  |            |            |           |
|            |        |  r - one section, opens on the right side |            |            |           |
|            |        |  2 - two sections                         |            |            |           |
+------------+--------+-------------------------------------------+------------+------------+-----------+


Examples
--------

::

        "rack": {
            "depth": 600,
            "front_door": "l",
            "rear_door": "c",
            "units": 4,
            "width": 600
        }
