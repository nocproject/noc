.. _dev-modelinterface-splitter:

========================
splitter Model Interface
========================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

Split input power to outputs with given gain

Variables
---------

+--------+--------+-------------------------------------------------------------------+------------+------------+-----------+
| Name   | Type   | Description                                                       | Required   | Constant   | Default   |
+========+========+===================================================================+============+============+===========+
| split  | str    | Input power division, as comma-separated list of output_Name=gain | True       | True       |           |
+--------+--------+-------------------------------------------------------------------+------------+------------+-----------+




Examples
--------

splitter 1 to 2 with 50/50 share power
::
    split: "out1=0.5,out2=0.5"

splitter 1 to 3 with 50%/25%/25% share power
::
    split: "out1=0.5,out2=0.25,out3=0.25"

splitter 1 to 2 with signal multiplication 3dB
::
    split: "out1=2,out2=2"
