.. _man-confdb:

======
confdb
======

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Name
----
`noc confdb` - ConfDB manipulation tool

Synopsis
--------

    noc confdb syntax [path ...]
               tokenizer [--object=<id>|--profile=<profile> --config=<path>]
               normalizer [--object=<id>|--profile=<profile> --config=<path>]

Description
-----------
ConfDB investigation tool

Examples
--------

Dump ConfDB syntax:

.. code-block:: text

    ./noc confdb syntax

Dump part of ConfDB syntax:

.. code-block:: text

    ./noc confdb syntax intefaces x

Dump result of object's :ref:`tokenizer<dev-confdb-tokenizer>`.
Managed Object ID is 120:

.. code-block:: text

    ./noc confdb tokenizer --object=120

Dump result of object's :ref:`tokenizer<dev-confdb-tokenizer>`,
applied to arbitrary file:

.. code-block:: text

    ./noc confdb tokenizer --object=120 --config=config.txt

Dump result of profile's :ref:`tokenizer<dev-confdb-tokenizer>`,
applied to arbitrary file:

.. code-block:: text

    ./noc confdb tokenizer --profile=Cisco.IOS --config=config.txt

Dump result of object's :ref:`normalizer<dev-confdb-normalizer>`.
Managed Object ID is 120:

.. code-block:: text

    ./noc confdb normalizer --object=120

Dump result of object's :ref:`normalizer<dev-confdb-normalizer>`,
applied to arbitrary file:

.. code-block:: text

    ./noc confdb normalizer --object=120 --config=config.txt

Dump result of profile's :ref:`normalizer<dev-confdb-normalizer>`,
applied to arbitrary file:

.. code-block:: text

    ./noc confdb normalizer --profile=Cisco.IOS --config=config.txt

See also
--------
* :ref:`ConfDB Syntax Reference <dev-confdb-syntax>`
* :ref:`ConfDB Normalizers <dev-confdb-normalizer>`
* :ref:`ConfDB Tokenizers <dev-confdb-tokenizer>`
