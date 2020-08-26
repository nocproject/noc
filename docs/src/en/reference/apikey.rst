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

Example: `curl  -s -D - -k -H 'Private-Token: 12345'  https://noc_url/api/datastream/managedobject` ,
where 12345 is an API token key.

Roles
-----

.. _reference-apikey-roles-datastream:

datastream API
^^^^^^^^^^^^^^
Access to :ref:`api-datastream`

+-----------------------------------+------------------------------------------------------------------------------------+
| API:Role                          | Description                                                                        |
+===================================+====================================================================================+
| `datastream:administrativedomain` | :ref:`administrativedomain datastream <api-datastream-administrativedomain>` access|
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:alarm`                | :ref:`alarm datastream <api-datastream-alarm>` access                              |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:resourcegroup`        | :ref:`resourcegroup datastream <api-datastream-resourcegroup>` access              |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:managedobject`        | :ref:`managedobject datastream <api-datastream-managedobject>` access              |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:dnszone`              | :ref:`dnszone datastream <api-datastream-dnszone>` access                          |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:cfgping`              | :ref:`cfgping datastream <api-datastream-cfgping>` access                          |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:cfgsyslog`            | :ref:`cfgsyslog datastream <api-datastream-cfgsyslog>` access                      |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:cfgtrap`              | :ref:`cfgtrap datastream <api-datastream-cfgtrap>` access                          |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:vrf`                  | :ref:`vrf datastream <api-datastream-vrf>` access                                  |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:prefix`               | :ref:`prefix datastream <api-datastream-prefix>` access                            |
+-----------------------------------+------------------------------------------------------------------------------------+
| `datastream:address`              | :ref:`address datastream <api-datastream-address>` access                          |
+-----------------------------------+------------------------------------------------------------------------------------+

.. _reference-apikey-roles-nbi:

NBI API
^^^^^^^

+-----------------------+----------------------------------------------------------------+
| API:Role              | Description                                                    |
+=======================+================================================================+
| `nbi:config`          | :ref:`NBI config API <api-nbi-config>` access                  |
+-----------------------+----------------------------------------------------------------+
| `nbi:configrevisions` | :ref:`NBI configrevisions API <api-nbi-configrevisions>` access|
+-----------------------+----------------------------------------------------------------+
| `nbi:getmappings`     | :ref:`NBI getmappings API <api-nbi-getmappings>` access        |
+-----------------------+----------------------------------------------------------------+
| `nbi:objectmetrics`   | :ref:`NBI objectmetrics API <api-nbi-objectmetrics>` access    |
+-----------------------+----------------------------------------------------------------+
| `nbi:objectstatus`    | :ref:`NBI objectstatus API <api-nbi-objectstatus>` access      |
+-----------------------+----------------------------------------------------------------+
| `nbi:path`            | :ref:`NBI path API <api-nbi-path>` access                      |
+-----------------------+----------------------------------------------------------------+
| `nbi:telemetry`       | :ref:`NBI telemetry API <api-nbi-telemetry>` access            |
+-----------------------+----------------------------------------------------------------+

.. _reference-apikey-web-interface:

Web interface example
---------------------

You should fill `Name` and `API key` as required fields.
Also in `API` rows should be `nbi`  or `datastream`. In `Role` row should be a role from tables above or `*` (asterisk)

.. image:: /images/apikey_edit_api.png

You can fill the ACL section or may leave it empty.
Prefix field should be in a IP/net way.

.. image:: /images/apikey_edit_api_acl.png

Also there is an opportunity to allow requests to API only from whitelist IPs.
You can find this option in Tower, in `nbi`/`datastream` service respectively.

.. _reference-apikey-best-practices:

Best Practices
--------------
* Grant separate API Keys for every connected system
* Grant separate API Keys for every developer, Restrict key lifetime
* Grant separate API Keys for every external tester, Restrict key to short lifetime
