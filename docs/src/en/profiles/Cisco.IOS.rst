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

Show firmware version
^^^^^^^^^^^^^^^^^^^^^

.. code-block::

    show version

Show platform
^^^^^^^^^^^^^

.. code-block::

    show version

Show configuration
^^^^^^^^^^^^^^^^^^
Show current running configuration

.. code-block::

    show running-config

Show startup configuration

.. code-block::

    show startup-config

Entering Configuration Mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^

All configuration commands are entered in the configuration mode.
To enter configuration mode type

.. code-block:: text

    configure terminal

Save Configuration
^^^^^^^^^^^^^^^^^^

To save configuration changes type

.. code-block::

    copy running-config startup-config


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

.. _profile-Cisco.IOS-used:

Used Commands
-------------
`Cisco.IOS` profile emmits following commands. Ensure they are
available for NOC user:

* show version
* show running-config
* show startup-config
...
