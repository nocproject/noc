.. _dev-modelinterface-airflow:

=======================
airflow Model Interface
=======================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Airflow direction for cooling. May be set for rack to show desired
airflow movement from *cold* to *hot* area, and for equipment to show
constructive air movement

Variables
---------

+---------+--------+---------------------------+----------+----------+---------+
| Name    | Type   | Description               | Required | Constant | Default |
+---------+--------+---------------------------+----------+----------+---------+
| inlet   | String | Direction of cold inlet:  | No       | No       |         |
|         |        |                           |          |          |         |
|         |        | * *f* - forward           |          |          |         |
|         |        | * *r* - rear              |          |          |         |
|         |        | * *b* - bottom            |          |          |         |
|         |        | * *t* - top               |          |          |         |
|         |        | * *l* - left              |          |          |         |
|         |        | * *r* - right             |          |          |         |
+---------+--------+---------------------------+----------+----------+---------+
| exhaust | String | Direction of hot exhaust: | No       | No       |         |
|         |        |                           |          |          |         |
|         |        | * *f* - forward           |          |          |         |
|         |        | * *r* - rear              |          |          |         |
|         |        | * *b* - bottom            |          |          |         |
|         |        | * *t* - top               |          |          |         |
|         |        | * *l* - left              |          |          |         |
|         |        | * *r* - right             |          |          |         |
+---------+--------+---------------------------+----------+----------+---------+

Examples
--------

::

    "airflow": {
        "exhaust": "l",
        "intake": "r"
    }