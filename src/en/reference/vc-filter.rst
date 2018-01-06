=========
VC Filter
=========

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

*VC Filter* is named VLAN filters which can be reused in many places

Expression Syntax
-----------------
*VC Filter* expression syntax::

    <vcfilter> ::= <item> [',' <vcfilter>]
    <item> ::= <vlan> | <range>
    <vlan> ::= [0-9]+
    <range> ::= <vlan> '-' <vlan>

Examples
--------
::

    1
    1-100
    1-100,105,200-210
