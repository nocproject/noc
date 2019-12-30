.. _dev-confdb-syntax-virtual-router:

virtual-router
^^^^^^^^^^^^^^

========  ==
Parent    -
Required  No
Multiple  No
Default:  -
========  ==


Contains:

+------------------------------------------------+------------+---------+
| Node                                           | Required   | Multi   |
+================================================+============+=========+
| :ref:`vr<dev-confdb-syntax-virtual-router-vr>` | Yes        | No      |
+------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr:

virtual-router \*<vr>
^^^^^^^^^^^^^^^^^^^^^

========  =======================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router>`
Required  Yes
Multiple  Yes
Default:  default
Name      vr
========  =======================================================


Contains:

+-------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                | Required   | Multi   |
+=====================================================================================+============+=========+
| :ref:`forwarding-instance<dev-confdb-syntax-virtual-router-vr-forwarding-instance>` | Yes        | Yes     |
+-------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance:

virtual-router \*<vr> forwarding-instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr>`
Required  Yes
Multiple  No
Default:  -
========  ==========================================================


Contains:

+-----------------------------------------------------------------------------------+------------+---------+
| Node                                                                              | Required   | Multi   |
+===================================================================================+============+=========+
| :ref:`instance<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>` | Yes        | No      |
+-----------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance:

virtual-router \*<vr> forwarding-instance \*<instance>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance>`
Required  Yes
Multiple  Yes
Default:  default
Name      instance
========  ==============================================================================


Contains:

+------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                             | Required   | Multi   |
+==================================================================================================================+============+=========+
| :ref:`type<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-type>`                               | No         | Yes     |
+------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`description<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-description>`                 | No         | Yes     |
+------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`route-distinguisher<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-distinguisher>` | No         | Yes     |
+------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`vrf-target<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target>`                   | No         | Yes     |
+------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`vpn-id<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vpn-id>`                           | No         | Yes     |
+------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`vlans<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans>`                             | No         | Yes     |
+------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`interfaces<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces>`                   | No         | Yes     |
+------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`route<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route>`                             | No         | Yes     |
+------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`protocols<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`                     | No         | Yes     |
+------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-type:

virtual-router \*<vr> forwarding-instance \*<instance> type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+-----------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                    | Required   | Multi   |
+=========================================================================================+============+=========+
| :ref:`type<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-type-type>` | Yes        | No      |
+-----------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-type-type:

virtual-router \*<vr> forwarding-instance \*<instance> type <type>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-type>`
Required  Yes
Multiple  No
Default:  -
Name      type
========  ============================================================================================


.. py:function:: make_forwarding_instance_type(type)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> type <type>` node

    :param type: virtual-router \*<vr> forwarding-instance \*<instance> type

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-description:

virtual-router \*<vr> forwarding-instance \*<instance> description
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                         | Required   | Multi   |
+==============================================================================================================+============+=========+
| :ref:`description<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-description-description>` | No         | No      |
+--------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-description-description:

virtual-router \*<vr> forwarding-instance \*<instance> description <description>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-description>`
Required  No
Multiple  No
Default:  -
Name      description
========  ===================================================================================================


.. py:function:: make_forwarding_instance_description(description)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> description <description>` node

    :param description: virtual-router \*<vr> forwarding-instance \*<instance> description

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-distinguisher:

virtual-router \*<vr> forwarding-instance \*<instance> route-distinguisher
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+----------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                               | Required   | Multi   |
+====================================================================================================+============+=========+
| :ref:`rd<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-distinguisher-rd>` | Yes        | No      |
+----------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-distinguisher-rd:

virtual-router \*<vr> forwarding-instance \*<instance> route-distinguisher <rd>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-distinguisher>`
Required  Yes
Multiple  No
Default:  -
Name      rd
========  ===========================================================================================================


.. py:function:: make_forwarding_instance_rd(rd)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> route-distinguisher <rd>` node

    :param rd: virtual-router \*<vr> forwarding-instance \*<instance> route-distinguisher

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target:

virtual-router \*<vr> forwarding-instance \*<instance> vrf-target
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+---------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                              | Required   | Multi   |
+===================================================================================================+============+=========+
| :ref:`import<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-import>` | No         | No      |
+---------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`export<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-export>` | No         | No      |
+---------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-import:

virtual-router \*<vr> forwarding-instance \*<instance> vrf-target import
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target>`
Required  No
Multiple  No
Default:  -
========  ==================================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                     | Required   | Multi   |
+==========================================================================================================+============+=========+
| :ref:`target<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-import-target>` | No         | No      |
+----------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-import-target:

virtual-router \*<vr> forwarding-instance \*<instance> vrf-target import \*<target>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-import>`
Required  No
Multiple  Yes
Default:  -
Name      target
========  =========================================================================================================


.. py:function:: make_forwarding_instance_import_target(target)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> vrf-target import \*<target>` node

    :param target: virtual-router \*<vr> forwarding-instance \*<instance> vrf-target import

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-export:

virtual-router \*<vr> forwarding-instance \*<instance> vrf-target export
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target>`
Required  No
Multiple  No
Default:  -
========  ==================================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                     | Required   | Multi   |
+==========================================================================================================+============+=========+
| :ref:`target<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-export-target>` | No         | No      |
+----------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-export-target:

virtual-router \*<vr> forwarding-instance \*<instance> vrf-target export \*<target>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vrf-target-export>`
Required  No
Multiple  Yes
Default:  -
Name      target
========  =========================================================================================================


.. py:function:: make_forwarding_instance_export_target(target)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> vrf-target export \*<target>` node

    :param target: virtual-router \*<vr> forwarding-instance \*<instance> vrf-target export

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vpn-id:

virtual-router \*<vr> forwarding-instance \*<instance> vpn-id
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+-----------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                          | Required   | Multi   |
+===============================================================================================+============+=========+
| :ref:`vpn_id<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vpn-id-vpn_id>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vpn-id-vpn_id:

virtual-router \*<vr> forwarding-instance \*<instance> vpn-id <vpn_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vpn-id>`
Required  Yes
Multiple  No
Default:  -
Name      vpn_id
========  ==============================================================================================


.. py:function:: make_forwarding_instance_vpn_id(vpn_id)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> vpn-id <vpn_id>` node

    :param vpn_id: virtual-router \*<vr> forwarding-instance \*<instance> vpn-id

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans:

virtual-router \*<vr> forwarding-instance \*<instance> vlans
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                           | Required   | Multi   |
+================================================================================================+============+=========+
| :ref:`vlan_id<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id>` | No         | No      |
+------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id:

virtual-router \*<vr> forwarding-instance \*<instance> vlans \*<vlan_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans>`
Required  No
Multiple  Yes
Default:  -
Name      vlan_id
========  =============================================================================================


.. py:function:: make_vlan_id(vlan_id)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> vlans \*<vlan_id>` node

    :param vlan_id: virtual-router \*<vr> forwarding-instance \*<instance> vlans


Contains:

+----------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                           | Required   | Multi   |
+================================================================================================================+============+=========+
| :ref:`name<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-name>`               | No         | Yes     |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`description<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-description>` | No         | Yes     |
+----------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-name:

virtual-router \*<vr> forwarding-instance \*<instance> vlans \*<vlan_id> name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id>`
Required  No
Multiple  No
Default:  -
========  =====================================================================================================


Contains:

+-------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                  | Required   | Multi   |
+=======================================================================================================+============+=========+
| :ref:`name<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-name-name>` | Yes        | No      |
+-------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-name-name:

virtual-router \*<vr> forwarding-instance \*<instance> vlans \*<vlan_id> name <name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-name>`
Required  Yes
Multiple  No
Default:  -
Name      name
========  ==========================================================================================================


.. py:function:: make_vlan_name(name)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> vlans \*<vlan_id> name <name>` node

    :param name: virtual-router \*<vr> forwarding-instance \*<instance> vlans \*<vlan_id> name

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-description:

virtual-router \*<vr> forwarding-instance \*<instance> vlans \*<vlan_id> description
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id>`
Required  No
Multiple  No
Default:  -
========  =====================================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                       | Required   | Multi   |
+============================================================================================================================+============+=========+
| :ref:`description<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-description-description>` | Yes        | No      |
+----------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-description-description:

virtual-router \*<vr> forwarding-instance \*<instance> vlans \*<vlan_id> description <description>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-vlans-vlan_id-description>`
Required  Yes
Multiple  No
Default:  -
Name      description
========  =================================================================================================================


.. py:function:: make_vlan_description(description)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> vlans \*<vlan_id> description <description>` node

    :param description: virtual-router \*<vr> forwarding-instance \*<instance> vlans \*<vlan_id> description

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+---------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                    | Required   | Multi   |
+=========================================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface>` | Yes        | No      |
+---------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces>`
Required  Yes
Multiple  Yes
Default:  -
Name      interface
========  ==================================================================================================


Contains:

+---------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                    | Required   | Multi   |
+=========================================================================================================+============+=========+
| :ref:`unit<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit>` | No         | Yes     |
+---------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  ============================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                         | Required   | Multi   |
+==============================================================================================================+============+=========+
| :ref:`unit<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit>` | No         | No      |
+--------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit>`
Required  No
Multiple  Yes
Default:  0
Name      unit
========  =================================================================================================================


Contains:

+---------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                            | Required   | Multi   |
+=================================================================================================================================+============+=========+
| :ref:`description<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-description>` | No         | Yes     |
+---------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`inet<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet>`               | No         | Yes     |
+---------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`inet6<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6>`             | No         | Yes     |
+---------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`iso<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-iso>`                 | No         | Yes     |
+---------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`mpls<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-mpls>`               | No         | Yes     |
+---------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`bridge<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge>`           | No         | Yes     |
+---------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-description:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> description
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================================


Contains:

+---------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                        | Required   | Multi   |
+=============================================================================================================================================+============+=========+
| :ref:`description<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-description-description>` | Yes        | No      |
+---------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-description-description:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> description <description>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-description>`
Required  Yes
Multiple  No
Default:  -
Name      description
========  ==================================================================================================================================


.. py:function:: make_unit_description(description)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> description <description>` node

    :param description: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> description

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> inet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                         | Required   | Multi   |
+==============================================================================================================================+============+=========+
| :ref:`address<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet-address>` | No         | No      |
+------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet-address:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> inet address
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet>`
Required  No
Multiple  No
Default:  -
========  ===========================================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                 | Required   | Multi   |
+======================================================================================================================================+============+=========+
| :ref:`address<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet-address-address>` | No         | No      |
+--------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet-address-address:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> inet address \*<address>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet-address>`
Required  No
Multiple  Yes
Default:  -
Name      address
========  ===================================================================================================================================


.. py:function:: make_unit_inet_address(address)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> inet address \*<address>` node

    :param address: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> inet address

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> inet6
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================================


Contains:

+-------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                          | Required   | Multi   |
+===============================================================================================================================+============+=========+
| :ref:`address<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6-address>` | No         | No      |
+-------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6-address:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> inet6 address
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6>`
Required  No
Multiple  No
Default:  -
========  ============================================================================================================================


Contains:

+---------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                  | Required   | Multi   |
+=======================================================================================================================================+============+=========+
| :ref:`address<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6-address-address>` | No         | No      |
+---------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6-address-address:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> inet6 address \*<address>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-inet6-address>`
Required  No
Multiple  Yes
Default:  -
Name      address
========  ====================================================================================================================================


.. py:function:: make_unit_inet6_address(address)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> inet6 address \*<address>` node

    :param address: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> inet6 address

