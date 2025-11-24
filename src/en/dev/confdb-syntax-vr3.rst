.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-stack-stack:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> stack <stack>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-stack>`
Required  Yes
Multiple  No
Default:  0
Name      stack
========  =======================================================================================================================================


.. py:function:: make_input_vlan_map_stack(stack)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> stack <stack>` node

    :param stack: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> stack

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-outer_vlans:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> outer_vlans
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                                   | Required   | Multi   |
+========================================================================================================================================================+============+=========+
| :ref:`vlan_filter<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-outer_vlans-vlan_filter>` | No         | No      |
+--------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-outer_vlans-vlan_filter:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> outer_vlans \*<vlan_filter>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-outer_vlans>`
Required  No
Multiple  Yes
Default:  -
Name      vlan_filter
========  =============================================================================================================================================


.. py:function:: make_input_vlan_map_outer_vlans(vlan_filter)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> outer_vlans \*<vlan_filter>` node

    :param vlan_filter: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> outer_vlans

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-inner_vlans:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> inner_vlans
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                                   | Required   | Multi   |
+========================================================================================================================================================+============+=========+
| :ref:`vlan_filter<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-inner_vlans-vlan_filter>` | No         | No      |
+--------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-inner_vlans-vlan_filter:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> inner_vlans \*<vlan_filter>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-inner_vlans>`
Required  No
Multiple  Yes
Default:  -
Name      vlan_filter
========  =============================================================================================================================================


.. py:function:: make_input_vlan_map_inner_vlans(vlan_filter)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> inner_vlans \*<vlan_filter>` node

    :param vlan_filter: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> inner_vlans

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> \*<op_num>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num>`
Required  No
Multiple  Yes
Default:  -
Name      op_num
========  =================================================================================================================================


Contains:

+---------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                            | Required   | Multi   |
+=================================================================================================================================+============+=========+
| :ref:`op<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num-op>` | Yes        | Yes     |
+---------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num-op:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> \*<op_num> <op>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num>`
Required  Yes
Multiple  No
Default:  -
Name      op
========  ========================================================================================================================================


.. py:function:: make_input_vlan_map_rewrite_operation(op)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> \*<op_num> <op>` node

    :param op: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> \*<op_num>


Contains:

+----------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                   | Required   | Multi   |
+========================================================================================================================================+============+=========+
| :ref:`vlan<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num-op-vlan>` | No         | No      |
+----------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num-op-vlan:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> \*<op_num> <op> <vlan>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-num-op_num-op>`
Required  No
Multiple  No
Default:  -
Name      vlan
========  ===========================================================================================================================================


.. py:function:: make_input_vlan_map_rewrite_vlan(vlan)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> \*<op_num> <op> <vlan>` node

    :param vlan: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge \*<num> \*<op_num> <op>

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

