.. _reference-apikey:

=======
API Key
=======

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

:todo:
    Describe API Key concept

.. _reference-apikey-usage:

Usage
-----
Client *MUST* set `Private-Token` HTTP Request header and set it
with proper *Key* in order to get access to protected API

Roles
-----

.. _reference-apikey-roles-datastream:

datastream API
^^^^^^^^^^^^^^
Access to :ref:`api-datastream`

+-----------------------------------+-----------------------------------------------------------------------------------+
| API:Role                          | Description                                                                       |
+===================================+===================================================================================+
| `datastream:administrativedomain` | ref:`administrativedomain datastream<api-datastream-administrativedomain>` access |
+-----------------------------------+-----------------------------------------------------------------------------------+
| `datastream:alarm`                | ref:`alarm datastream<api-datastream-alarm>` access                               |
+-----------------------------------+-----------------------------------------------------------------------------------+
| `datastream:resourcegroup`        | ref:`resourcegroup datastream<api-datastream-resourcegroup>` access               |
+-----------------------------------+-----------------------------------------------------------------------------------+
| `datastream:managedobject`        | ref:`managedobject datastream<api-datastream-managedobject>` access               |
+-----------------------------------+-----------------------------------------------------------------------------------+
| `datastream:dnszone`              | ref:`dnszone datastream<api-datastream-dnszone>` access                           |
+-----------------------------------+-----------------------------------------------------------------------------------+
| `datastream:cfgping`              | ref:`cfgping datastream<api-datastream-cfgping>` access                           |
+-----------------------------------+-----------------------------------------------------------------------------------+
| `datastream:cfgsyslog`            | ref:`cfgsyslog datastream<api-datastream-cfgsyslog>` access                       |
+-----------------------------------+-----------------------------------------------------------------------------------+
| `datastream:cfgtrap`              | ref:`cfgtrap datastream<api-datastream-cfgtrap>` access                           |
+-----------------------------------+-----------------------------------------------------------------------------------+

.. _reference-apikey-roles-nbi:

NBI API
^^^^^^^

+---------------------+-----------------------------------------------------------+
| API:Role            | Description                                               |
+=====================+===========================================================+
| `nbi:objectmetrics` | ref:`NBI objectmetrics API<api-nbi-objectmetrics>` access |
+---------------------+-----------------------------------------------------------+

Best Practices
--------------
* Grant separate API Keys for every connected system
* Grant separate API Keys for every developer, Restrict key lifetime
* Grant separate API Keys for every external tester, Restrict key to short lifetime
