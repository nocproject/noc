.. _bi-model-mac:

=========
mac model
=========

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

.. todo::
    Describe *mac* bi model

Table Structure
---------------

============== ==========================================================
**Table Name** mac
**Engine**     MergeTree(date, (managed_object, ts), 8192)
============== ==========================================================

========================= ==================== ==================================================
Field                     Data Type            Description
========================= ==================== ==================================================
date                      Date                 Date
ts                        DateTime             Created
managed_object            UInt64               Object Name
interface                 String               Physical Interface
subinterface              String               Logical Interface
neighbor_address          String               Neighbor Address
neighbor_object           UInt64               Neighbor Object
protocol                  String               Protocol
bgp_local_as              UInt64               BGP Local AS
bgp_remote_as             UInt64               BGP Remogte AS
========================= ==================== ==================================================
