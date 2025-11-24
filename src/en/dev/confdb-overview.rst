.. _dev-confdb-overview:

===============
ConfDB Overview
===============

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

`ConfDB` is a common term for complex of measures for high-level device configuration
processing within NOC. Vendors tend to invent own configuration
formats, often mimicking each other, and to introduce incompatibilities
between releases and platforms. Besides simple change tracking and
regular expression search, the multi-vendor configuration processing
may be very challenging task.

NOC addresses the challenge with following approach:

* *Decomposition* - complex task may be split to simple steps
* *Reusability* - all tools may be reused whenever possible
* *Pipelining* - each steps combined together into configuration processing pipelines
* *Clean contract between steps* - each step performs own task. Steps accept
  predictable result from previous steps and pass predictable result to following steps
* *Clean API* - each step must be understandable and easy to implement
* *Quick result* - First result must be reached easily and quickly. Then you can became to
  implement more complex things

To better understand the concept of `ConfDB` one should refer
to widely-used concept in programming languages - `Virtual Machines`.
`Virtual Machine` (VM) is the fictional computer with own `native assembly`
language (or machine codes). Its sometimes easier to break the
task of compiling the program from programming language to target
processor to two steps: to compile to fictional machine codes and
to compile from fictional codes to target ones. The benefits in clear
separation of common functions, suitable for all target platforms,
and of specific functions, addressed for single platform. Common functions
moved to the left (Code -> VM translation), while specific moved to
the right (VM -> Target platform translation). Hence VM represents
clean contract between hardware-dependent and hardware independent functions.

Device configuration is the programming language of target platform.
So we can split the task of configuration analysis by applying
clean barrier between hardware-dependent and hardware-independent parts.
Just like `Virtual Machine` NOC introduces fictional configuration
language for non-existing (yet?) network equipment. All hardware-dependent
parts are moved to the left. All hardware-independent parts are moved
to the right and may be reused.

ConfDB pipeline stages
----------------------
Config processing pipeline and stages are represented on chart below

.. mermaid::

    graph TD
        Fetching --> Storing
        Storing --> Tokenizer
        Tokenizer --> Normalizer
        Normalizer --> Applicator
        Applicator --> ConfDB
        ConfDB --> Queries


* :ref:`Fetching<dev-confdb-fetching>`
* :ref:`Storing<dev-confdb-storage>`
* :ref:`Tokenizer<dev-confdb-tokenizer>`
* :ref:`Normalizer<dev-confdb-normalizer>`
* Applicator
* ConfDB engine
* ConfDB queries