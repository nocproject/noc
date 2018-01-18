.. _bi-model-reboots:

=============
reboots model
=============

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

.. todo::
    Describe *reboots* bi model

Table Structure
---------------

============== ==========================================================
**Table Name** reboots
**Engine**     MergeTree(date, (ts, managed_object), 8192)
============== ==========================================================

========================= ==================== ==================================================
Field                     Data Type            Description
========================= ==================== ==================================================
date                      Date                 Date
ts                        DateTime             Created
managed_object            UInt64               Object Name
pool                      UInt64               Pool Name
ip                        UInt32               IP Address
profile                   UInt64               Profile
vendor                    UInt64               Vendor Name
platform                  UInt64               Platform
version                   UInt64               Version
administrative_domain     UInt64               Admin. Domain
segment                   UInt64               Network Segment
container                 UInt64               Container
x                         Float64              Longitude
y                         Float64              Latitude
========================= ==================== ==================================================
