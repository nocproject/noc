.. _man-datastream:

==========
datastream
==========

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Name
----
*datastream*: DataStream manipulation tool

Synopsis
--------
::

    noc datastream list
    noc datastream rebuild --datastream=<name>

Description
-----------
list
^^^^
List all existent datastreams

::

    noc datastream list

rebuild
^^^^^^^
Recalculate datastream `<name>`

::

    noc datastream rebuild --datastream=<name>


Examples
--------
::

    /opt/noc$ ./noc datastream list
    /opt/noc$ ./noc datastream rebuild --datastream=cfgping

See also
--------
* :ref:`api-datastream`
