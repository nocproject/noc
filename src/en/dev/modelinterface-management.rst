.. _dev-modelinterface-management:

==========================
management Model Interface
==========================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

ManagedObject binding
Binding inventory object with Managed Object(MO) Service Activation(SA)
One MO can be associated with several inventory objects(virtual chassis, switches in the stack)

Variables
---------

+----------------+--------+-----------------------------------------+------------+------------+-----------+
| Name           | Type   | Description                             | Required   | Constant   | Default   |
+================+========+=========================================+============+============+===========+
| managed        | bool   | Object can be bind to the ManagedObject | False      | True       |           |
+----------------+--------+-----------------------------------------+------------+------------+-----------+
| managed_object | int    | Managed Object id                       | False      | False      |           |
+----------------+--------+-----------------------------------------+------------+------------+-----------+



Examples
--------

::

    "management": {
         "managed": true
    }