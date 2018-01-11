.. _man-config:

======
config
======

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Name
----
*config*: Config manipulation tool

Synopsis
--------
::

    noc config dump

Description
-----------
*config* loads effective configuration and dumps it in YAML format to stdout.
Effective configuration defined by :ref:`noc_config` environment variable.
Refer to :ref:`admin-configuration` for details.

Examples
--------
::

    /opt/noc$ ./noc config dump
    /opt/noc$ NOC_CONFIG=legacy:/// ./noc config dump

See also
--------
* :ref:`noc_config`
* :ref:`admin-configuration`
