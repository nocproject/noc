.. _dev-confdb-fetching:

===============
Config Fetching
===============

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

`Fetching` is the process of retrieving of device configuration.
Performed by :ref:`config check<discovery-check-config>` of :ref:`box discovery<discovery-box>`.
According to the `Config Policy` setting in :ref:`Managed Object Profile<reference-managed-object-profile>`
there are two method possible:

* Script
* Download from external storage

Fetching via script
-------------------
:ref:`get_config<script-get_config>` script for target platform is necessary.
Usually it is the second script besides :ref:`get_version<script-get_version>` to implement.

Fetching from external storage
------------------------------
`Discovery` can download configuration from :ref:`External Storage<reference-external-storage>`.
Supposed that configuration supplied to storage via external process:
device uploads config by itself or some third-party system (like RANCID),
performs all dirty work for us. Fetching from external storage is
the integrated feature of `Discovery` and provided out-of-the box.
