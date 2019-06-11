.. _dev-modelinterface-sector:

======================
sector Model Interface
======================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Antenna sector, it is usually used in a combination about a :ref:`dev-modelinterface-geopoint`.

Variables
---------

+-------------+--------+----------------------------------+------------+------------+-----------+
| Name        | Type   | Description                      | Required   | Constant   | Default   |
+=============+========+==================================+============+============+===========+
| bearing     | float  | Bearing angle                    | True       | False      |           |
+-------------+--------+----------------------------------+------------+------------+-----------+
| elevation   | float  | Elevation angle                  | True       | False      | 0         |
+-------------+--------+----------------------------------+------------+------------+-----------+
| height      | float  | Height above ground (in meters)  | True       | False      | 0         |
+-------------+--------+----------------------------------+------------+------------+-----------+
| h_beamwidth | float  | Horizontal beamwidth (in angles) | True       | True       |           |
+-------------+--------+----------------------------------+------------+------------+-----------+
| v_beamwidth | float  | Vertical beamwidth (in angles)   | True       | True       |           |
+-------------+--------+----------------------------------+------------+------------+-----------+
