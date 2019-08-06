.. _dev-confdb-syntax:

=============
ConfDB Syntax
=============

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol

*Normalized Config* is the device-independent configuration representation.
Raw device config processed by *Config Tokenizer* and converted to
the list of *Tokens*. *Tokens* processed by *Config Normalizer*
and became *Normalized Config*.

Structure
---------

| **system** :ref:`(?)<dev-config-normalized-system>`
| | **hostname** :ref:`(?)<dev-config-normalized-system-hostname>`
| | | ``<hostname>`` :ref:`(?)<dev-config-normalized-system-hostname-hostname>`
| | **domain-name** :ref:`(?)<dev-config-normalized-system-domain-name>`
| | | ``<domain name>``
| | **prompt** :ref:`(?)<dev-config-normalized-system-prompt>`
| | | ``<prompt>``
| | **clock** :ref:`(?)<dev-config-normalized-system-clock>`
| | | **timezone**
| | | | ``<tz name>``
| | | **source**
| | | | ``<source>``
| :ref:`virtual-router<dev-config-normalized-virtual-router>`
| | ``<vr name>``
| | | **forwarding-instance**
| | | | ``<fi name>``
| | | | | **interfaces**
| | | | | | ``<interface name>``
| | | | | | | **decscription**
| | | | | | | | ``<interface description>``
| | | | | | | **unit**
| | | | | | | | ``<unit name>``
| | | | | | | | | **description**
| | | | | | | | | | ``<unit description>``
| | | | | | | | | **inet**
| | | | | | | | | | **address**
| | | | | | | | | | | ``<IPv4 address>``
| | | | | | | | | **inet6**
| | | | | | | | | | **address**
| | | | | | | | | | | ``<IPv6 address>``
| | | | | | | | | **iso**
| | | | | | | | | | **address**
| | | | | | | | | | | ``<ISO address>``
| | | | | | | | | **bridge**
| | | | | | | | | | **port-security**
| | | | | | | | | | | **max-mac-count**
| | | | | | | | | | | | ``<max mac count>``
| | | | | **route**
| | | | | | **inet**
| | | | | | | **static**
| | | | | | | | ``<prefix>``
| | | | | | | | | **next-hop**
| | | | | | | | | | ``<address>``
| | | | | | **inet6**
| | | | | | | **static**
| | | | | | | | ``<prefix>``
| | | | | | | | | **next-hop**
| | | | | | | | | | ``<address>``
| | | | | **protocols**
| | | | | | **spanning-tree**
| | | | | | | **interface**
| | | | | | | | ``<interface name>``
| | | | | | | | | **cost**
| | | | | | | | | | ``<interface cost>``
| | | | | | **ntp**
| | | | | | | ``<server name>``
| | | | | | | | **version**
| | | | | | | | | ``<version>``
| | | | | | | | **address**
| | | | | | | | | ``<address>``
| | | | | | | | **mode**
| | | | | | | | | ``<mode>``
| | | | | | | | **authentication**
| | | | | | | | | **type**
| | | | | | | | | | ``<type>``
| | | | | | | | | **key**
| | | | | | | | | | ``<key>``
| | | | | | | | **prefer**
| | | | | | | | **broadcast**
| | | | | | | | | **version**
| | | | | | | | | | ``<version>``
| | | | | | | | | **address**
| | | | | | | | | | ``<address>``
| | | | | | | | | **authentication**
| | | | | | | | | | **type**
| | | | | | | | | | | ``<type>``
| | | | | | | | | | **key**
| | | | | | | | | | | ``<key>``

.. _dev-config-normalized-system:

.system
^^^^^^^
System-wide settings

======== ===
Parent
Required No
Multiple No
======== ===

Contains:

+----------------------------------------------------------------------+----------+-------+
| Node                                                                 | Required | Multi |
+======================================================================+==========+=======+
| :ref:`.system.hostname<dev-config-normalized-system-hostname>`       | No       | No    |
+----------------------------------------------------------------------+----------+-------+
| :ref:`.system.domain-name<dev-config-normalized-system-domain-name>` | No       | No    |
+----------------------------------------------------------------------+----------+-------+
| :ref:`.prompt<dev-config-normalized-system-prompt>`                  | No       | No    |
+----------------------------------------------------------------------+----------+-------+
| :ref:`.clock<dev-config-normalized-system-clock>`                    | No       | No    |
+----------------------------------------------------------------------+----------+-------+

.. _dev-config-normalized-system-hostname:

.system.hostname
^^^^^^^^^^^^^^^^
System hostname settings

======== ============================================
Parent   :ref:`.system<dev-config-normalized-system>`
Required No
Multiple No
======== ============================================

Contains:

+----------------------------------------------------------------------------------+----------+-------+
| Node                                                                             | Required | Multi |
+==================================================================================+==========+=======+
| :ref:`.system.hostname.hostname<dev-config-normalized-system-hostname-hostname>` | Yes      | No    |
+----------------------------------------------------------------------------------+----------+-------+

.. _dev-config-normalized-system-hostname-hostname:

.system.hostname.<hostname>
^^^^^^^^^^^^^^^^^^^^^^^^^^^
System hostname value

======== ==============================================================
Parent   :ref:`.system.hostname<dev-config-normalized-system-hostname>`
Required Yes
Multiple No
======== ==============================================================


.. _dev-config-normalized-system-domain-name:

.system.domain-name
^^^^^^^^^^^^^^^^^^^

.. _dev-config-normalized-system-prompt:

.system.prompt
^^^^^^^^^^^^^^

.. _dev-config-normalized-system-clock:

.system.clock
^^^^^^^^^^^^^


.. _dev-config-normalized-virtual-router:

.virtual-router
^^^^^^^^^^^^^^^
