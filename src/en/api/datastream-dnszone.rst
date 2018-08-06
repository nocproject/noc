.. _api-datastream-dnszone:

==================
dnszone DataStream
==================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

dnszone DataStream contains summarized :ref:`DNS Zone<reference-dns-zone>`
state, including zone's serial and Resource Records.

Fields
------

+------------+------------------+-----------------------------------------------+
| Name       | Type             | Description                                   |
+============+==================+===============================================+
| id         | String           | :ref:`DNS Zone's<reference-dns-zone>` ID      |
+------------+------------------+-----------------------------------------------+
| name       | String           | Zone Name (Domain name)                       |
+------------+------------------+-----------------------------------------------+
| serial     | String           | Zone's serial                                 |
+------------+------------------+-----------------------------------------------+
| masters    | Array of String  | List of master nameservers                    |
+------------+------------------+-----------------------------------------------+
| slaves     | Array of String  | List of slave nameservers                     |
+------------+------------------+-----------------------------------------------+
| records    | Array of Object  | List of zone's resource records               |
+------------+------------------+-----------------------------------------------+
| * name     | String           | Record name                                   |
+------------+------------------+-----------------------------------------------+
| * type     | String           | Record type (i.e. A, NS, CNAME, ...)          |
+------------+------------------+-----------------------------------------------+
| * rdata    | String           | Record value                                  |
+------------+------------------+-----------------------------------------------+
| * ttl      | Integer          | (Optional) Record's time-to-live              |
+------------+------------------+-----------------------------------------------+
| * priority | Integer          | (Optional) Record's priority (for MX and SRV) |
+------------+------------------+-----------------------------------------------+

Filters
-------

.. function:: server(name)

    Restrict stream to zones belonging to server `name`

    :param name: Server name (i.e. `ns1.example.com`)

Access
------
:ref:`API Key<reference-apikey>` with `datastream:dnszone` permissions
required.
