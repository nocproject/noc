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

+-----------------------------------+------------------------------------------------------------------------------------+
| API:Role                          | Description                                                                        |
+===================================+====================================================================================+
| `datastream:administrativedomain` | ref:`administrativedomain datastream <api-datastream-administrativedomain>` access |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:alarm`                | ref:`alarm datastream <api-datastream-alarm>` access                               |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:resourcegroup`        | ref:`resourcegroup datastream <api-datastream-resourcegroup>` access               |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:managedobject`        | ref:`managedobject datastream <api-datastream-managedobject>` access               |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:dnszone`              | ref:`dnszone datastream <api-datastream-dnszone>` access                           |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:cfgping`              | ref:`cfgping datastream <api-datastream-cfgping>` access                           |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:cfgsyslog`            | ref:`cfgsyslog datastream <api-datastream-cfgsyslog>` access                       |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:cfgtrap`              | ref:`cfgtrap datastream <api-datastream-cfgtrap>` access                           |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:vrf`                  | ref:`vrf datastream <api-datastream-vrf>` access                                   |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:prefix`               | ref:`prefix datastream <api-datastream-prefix>` access                             |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:address`              | ref:`address datastream <api-datastream-address>` access                           |
+-----------------------------------+------------------------------------------------------------------------------------+

.. _reference-apikey-roles-nbi:

NBI API
^^^^^^^

+-----------------------+----------------------------------------------------------------+
| API:Role              | Description                                                    |
+===========================+============================================================+
| `nbi:config`          | ref:`NBI config API <api-nbi-config>` access                   |
+-----------------------+----------------------------------------------------------------+
| `nbi:configrevisions` | ref:`NBI configrevisions API <api-nbi-configrevisions>` access |
+-----------------------+----------------------------------------------------------------+
| `nbi:objectmetrics`   | ref:`NBI objectmetrics API <api-nbi-objectmetrics>` access     |
+-----------------------+----------------------------------------------------------------+
| `nbi:objectstatus`    | ref:`NBI objectstatus API <api-nbi-objectstatus>` access       |
+-----------------------+----------------------------------------------------------------+
| `nbi:path`            | ref:`NBI path API <api-nbi-path>` access                       |
+-----------------------+----------------------------------------------------------------+
| `nbi:telemetry`       | ref:`NBI telemetry API <api-nbi-telemetry>` access             |
+-----------------------+----------------------------------------------------------------+

.. _reference-apikey-best-practices:

Best Practices
--------------
* Grant separate API Keys for every connected system
* Grant separate API Keys for every developer, Restrict key lifetime
* Grant separate API Keys for every external tester, Restrict key to short lifetime
