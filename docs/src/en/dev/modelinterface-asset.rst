.. _dev-modelinterface-asset:

=====================
asset Model Interface
=====================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Inventory references, asset and serial numbers

Variables
---------

+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| Name            | Type        | Description                               | Required | Constant | Default |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| part_no         | String List | Internal vendor's part number             | Yes      | Yes      |         |
|                 |             | as shown by diagnostic commands           |          |          |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| order_part_no   | String List | Vendor's :term:`FRU` as shown             | No       | Yes      |         |
|                 |             | in catalogues and price lists             |          |          |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| serial          | String      | Item's serial number                      | No       |          |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| revision        | String      | Item's hardware revision                  | No       |          |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| asset_no        | String      | Item's asset number, used for             | No       |          |         |
|                 |             | asset tracking in accounting              |          |          |         |
|                 |             | system                                    |          |          |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| mfg_date        | String      | Manufacturing date in                     | No       |          |         |
|                 |             | YYYY-MM-DD format                         |          |          |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| cpe_22          | String      | CPE v2.2 identification string            | No       | Yes      |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| cpe_23          | String      | CPE v2.3 identification string            | No       | Yes      |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| min_serial_size | Integer     | Minimal valid serial number size          | No       | Yes      |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| max_serial_size | Integer     | Maximal valid serial number size          | No       | Yes      |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+
| serial_mask     | String      | Regular expression to check serial number | No       | Yes      |         |
+-----------------+-------------+-------------------------------------------+----------+----------+---------+

Examples
--------

::

    "asset": {
        "order_part_no": ["MX-MPC2E-3D-Q"],
        "part_no": ["750-038493"]
    }
