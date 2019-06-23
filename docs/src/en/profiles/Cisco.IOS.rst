.. _profile-Cisco.IOS:

=================
Cisco.IOS Profile
=================

.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 2
    :class: singlecol

`Cisco.IOS` profile supports wide range of
:ref:`Cisco Systems <profiles-vendor-Cisco>` network equipment running Cisco IOS software.

.. versionadded:: 0.1

.. _profile-Cisco.IOS-configuration:

Configuration
-------------

Create Local User
^^^^^^^^^^^^^^^^^

.. code-block:: text

    username <name> privelege 15 password <password>

Enable SNMP
^^^^^^^^^^^

Enable SSH
^^^^^^^^^^

Enable CDP
^^^^^^^^^^

Enable LLDP
^^^^^^^^^^^

.. _profile-Cisco.IOS-scripts:

Supported Scripts
-----------------

.. include:: ../include/auto/supported-scripts-Cisco.IOS.rst

.. _profile-Cisco.IOS-issues:

Known Issues
------------

* IOS 12.2SE got LLDP support starting from 12.2(33)SE, but
  due to several bugs it is recommended to use 12.2(50)SE or later
  if you planning to use LLDP discovery.

.. _profile-Cisco.IOS-platforms:

Supported Platforms
-------------------

.. include:: ../include/auto/supported-platforms-Cisco.IOS.rst
