.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-iso:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> iso
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================================


.. py:function:: make_unit_iso(None)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> iso` node

    :param None: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit>

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-mpls:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> mpls
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================================


.. py:function:: make_unit_mpls(None)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> mpls` node

    :param None: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit>

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                       | Required   | Multi   |
+============================================================================================================================================+============+=========+
| :ref:`switchport<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport>`       | No         | No      |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`port-security<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security>` | No         | No      |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`num<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num>`                     | Yes        | No      |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`num<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num>`                     | Yes        | No      |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`dynamic_vlans<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans>` | No         | No      |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge>`
Required  No
Multiple  No
Default:  -
========  =============================================================================================================================


Contains:

+---------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                        | Required   | Multi   |
+=============================================================================================================================================+============+=========+
| :ref:`untagged<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-untagged>` | No         | No      |
+---------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`native<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-native>`     | No         | No      |
+---------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`tagged<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-tagged>`     | No         | No      |
+---------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-untagged:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport untagged
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport>`
Required  No
Multiple  No
Default:  -
========  ========================================================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                                       | Required   | Multi   |
+============================================================================================================================================================+============+=========+
| :ref:`vlan_filter<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-untagged-vlan_filter>` | Yes        | No      |
+------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-untagged-vlan_filter:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport untagged \*<vlan_filter>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-untagged>`
Required  Yes
Multiple  Yes
Default:  -
Name      vlan_filter
========  =================================================================================================================================================


.. py:function:: make_switchport_untagged(vlan_filter)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport untagged \*<vlan_filter>` node

    :param vlan_filter: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport untagged

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-native:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport native
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport>`
Required  No
Multiple  No
Default:  -
========  ========================================================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                             | Required   | Multi   |
+==================================================================================================================================================+============+=========+
| :ref:`vlan_id<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-native-vlan_id>` | Yes        | No      |
+--------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-native-vlan_id:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport native <vlan_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-native>`
Required  Yes
Multiple  No
Default:  -
Name      vlan_id
========  ===============================================================================================================================================


.. py:function:: make_switchport_native(vlan_id)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport native <vlan_id>` node

    :param vlan_id: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport native

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-tagged:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport tagged
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport>`
Required  No
Multiple  No
Default:  -
========  ========================================================================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                                     | Required   | Multi   |
+==========================================================================================================================================================+============+=========+
| :ref:`vlan_filter<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-tagged-vlan_filter>` | Yes        | No      |
+----------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-tagged-vlan_filter:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport tagged \*<vlan_filter>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-switchport-tagged>`
Required  Yes
Multiple  Yes
Default:  -
Name      vlan_filter
========  ===============================================================================================================================================


.. py:function:: make_switchport_tagged(vlan_filter)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport tagged \*<vlan_filter>` node

    :param vlan_filter: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge switchport tagged

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge port-security
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge>`
Required  No
Multiple  No
Default:  -
========  =============================================================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                                     | Required   | Multi   |
+==========================================================================================================================================================+============+=========+
| :ref:`max-mac-count<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security-max-mac-count>` | No         | No      |
+----------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security-max-mac-count:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge port-security max-mac-count
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security>`
Required  No
Multiple  No
Default:  -
========  ===========================================================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                                   | Required   | Multi   |
+========================================================================================================================================================+============+=========+
| :ref:`limit<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security-max-mac-count-limit>` | Yes        | No      |
+--------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security-max-mac-count-limit:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge port-security max-mac-count <limit>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-port-security-max-mac-count>`
Required  Yes
Multiple  No
Default:  -
Name      limit
========  =========================================================================================================================================================


.. py:function:: make_unit_port_security_max_mac(limit)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge port-security max-mac-count <limit>` node

    :param limit: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge port-security max-mac-count

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge>`
Required  Yes
Multiple  Yes
Default:  -
Name      num
========  =============================================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                       | Required   | Multi   |
+============================================================================================================================================+============+=========+
| :ref:`stack<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-stack>`             | No         | Yes     |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`outer_vlans<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-outer_vlans>` | No         | Yes     |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`inner_vlans<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-inner_vlans>` | No         | Yes     |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`op_num<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num>`           | No         | Yes     |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-stack:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> stack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                 | Required   | Multi   |
+======================================================================================================================================+============+=========+
| :ref:`stack<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-stack-stack>` | Yes        | No      |
+--------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

