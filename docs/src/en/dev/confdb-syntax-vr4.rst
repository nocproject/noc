.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge dynamic_vlans
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge>`
Required  No
Multiple  No
Default:  -
========  =============================================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                                 | Required   | Multi   |
+======================================================================================================================================================+============+=========+
| :ref:`vlan_filter<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter>` | No         | No      |
+------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge dynamic_vlans \*<vlan_filter>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans>`
Required  No
Multiple  Yes
Default:  -
Name      vlan_filter
========  ===========================================================================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                                     | Required   | Multi   |
+==========================================================================================================================================================+============+=========+
| :ref:`service<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter-service>` | No         | Yes     |
+----------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter-service:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge dynamic_vlans \*<vlan_filter> service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                                             | Required   | Multi   |
+==================================================================================================================================================================+============+=========+
| :ref:`service<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter-service-service>` | No         | No      |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter-service-service:

virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge dynamic_vlans \*<vlan_filter> service <service>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-interfaces-interface-unit-unit-bridge-dynamic_vlans-vlan_filter-service>`
Required  No
Multiple  No
Default:  -
Name      service
========  ===============================================================================================================================================================


.. py:function:: make_interface_serivce_vlan(service)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge dynamic_vlans \*<vlan_filter> service <service>` node

    :param service: virtual-router \*<vr> forwarding-instance \*<instance> interfaces \*<interface> unit \*<unit> bridge dynamic_vlans \*<vlan_filter> service

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route:

virtual-router \*<vr> forwarding-instance \*<instance> route
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+--------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                       | Required   | Multi   |
+============================================================================================+============+=========+
| :ref:`inet<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet>`   | No         | No      |
+--------------------------------------------------------------------------------------------+------------+---------+
| :ref:`inet6<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6>` | No         | No      |
+--------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet:

virtual-router \*<vr> forwarding-instance \*<instance> route inet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route>`
Required  No
Multiple  No
Default:  -
========  =============================================================================================


Contains:

+---------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                              | Required   | Multi   |
+===================================================================================================+============+=========+
| :ref:`static<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static>` | No         | No      |
+---------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static:

virtual-router \*<vr> forwarding-instance \*<instance> route inet static
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet>`
Required  No
Multiple  No
Default:  -
========  ==================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                   | Required   | Multi   |
+========================================================================================================+============+=========+
| :ref:`route<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route>` | No         | No      |
+--------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route:

virtual-router \*<vr> forwarding-instance \*<instance> route inet static <route>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static>`
Required  No
Multiple  No
Default:  -
Name      route
========  =========================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                               | Required   | Multi   |
+====================================================================================================================+============+=========+
| :ref:`next-hop<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route-next-hop>` | No         | No      |
+--------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`discard<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route-discard>`   | No         | No      |
+--------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route-next-hop:

virtual-router \*<vr> forwarding-instance \*<instance> route inet static <route> next-hop
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                        | Required   | Multi   |
+=============================================================================================================================+============+=========+
| :ref:`next_hop<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route-next-hop-next_hop>` | No         | No      |
+-----------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route-next-hop-next_hop:

virtual-router \*<vr> forwarding-instance \*<instance> route inet static <route> next-hop \*<next_hop>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route-next-hop>`
Required  No
Multiple  Yes
Default:  -
Name      next_hop
========  ========================================================================================================================


.. py:function:: make_inet_static_route_next_hop(next_hop)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> route inet static <route> next-hop \*<next_hop>` node

    :param next_hop: virtual-router \*<vr> forwarding-instance \*<instance> route inet static <route> next-hop

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route-discard:

virtual-router \*<vr> forwarding-instance \*<instance> route inet static <route> discard
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet-static-route>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================================================


.. py:function:: make_inet_static_route_discard(None)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> route inet static <route> discard` node

    :param None: virtual-router \*<vr> forwarding-instance \*<instance> route inet static <route>

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6:

virtual-router \*<vr> forwarding-instance \*<instance> route inet6
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route>`
Required  No
Multiple  No
Default:  -
========  =============================================================================================


Contains:

+----------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                               | Required   | Multi   |
+====================================================================================================+============+=========+
| :ref:`static<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static>` | No         | No      |
+----------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static:

virtual-router \*<vr> forwarding-instance \*<instance> route inet6 static
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6>`
Required  No
Multiple  No
Default:  -
========  ===================================================================================================


Contains:

+---------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                    | Required   | Multi   |
+=========================================================================================================+============+=========+
| :ref:`route<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route>` | No         | No      |
+---------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route:

virtual-router \*<vr> forwarding-instance \*<instance> route inet6 static <route>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static>`
Required  No
Multiple  No
Default:  -
Name      route
========  ==========================================================================================================


Contains:

+---------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                | Required   | Multi   |
+=====================================================================================================================+============+=========+
| :ref:`next-hop<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route-next-hop>` | No         | No      |
+---------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route-next-hop:

virtual-router \*<vr> forwarding-instance \*<instance> route inet6 static <route> next-hop
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route>`
Required  No
Multiple  No
Default:  -
========  ================================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                         | Required   | Multi   |
+==============================================================================================================================+============+=========+
| :ref:`next_hop<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route-next-hop-next_hop>` | No         | No      |
+------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route-next-hop-next_hop:

virtual-router \*<vr> forwarding-instance \*<instance> route inet6 static <route> next-hop \*<next_hop>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-route-inet6-static-route-next-hop>`
Required  No
Multiple  Yes
Default:  -
Name      next_hop
========  =========================================================================================================================


.. py:function:: make_inet6_static_route_next_hop(next_hop)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> route inet6 static <route> next-hop \*<next_hop>` node

    :param next_hop: virtual-router \*<vr> forwarding-instance \*<instance> route inet6 static <route> next-hop

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols:

virtual-router \*<vr> forwarding-instance \*<instance> protocols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                           | Required   | Multi   |
+================================================================================================================+============+=========+
| :ref:`telnet<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-telnet>`               | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`ssh<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ssh>`                     | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`http<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-http>`                   | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`https<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-https>`                 | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`snmp<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp>`                   | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`isis<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis>`                   | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`ospf<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf>`                   | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`ldp<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp>`                     | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`rsvp<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp>`                   | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`pim<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim>`                     | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`igmp-snooping<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping>` | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-telnet:

virtual-router \*<vr> forwarding-instance \*<instance> protocols telnet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


.. py:function:: make_protocols_telnet(None)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols telnet` node

    :param None: virtual-router \*<vr> forwarding-instance \*<instance> protocols

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ssh:

virtual-router \*<vr> forwarding-instance \*<instance> protocols ssh
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


.. py:function:: make_protocols_ssh(None)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols ssh` node

    :param None: virtual-router \*<vr> forwarding-instance \*<instance> protocols

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-http:

virtual-router \*<vr> forwarding-instance \*<instance> protocols http
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


.. py:function:: make_protocols_http(None)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols http` node

    :param None: virtual-router \*<vr> forwarding-instance \*<instance> protocols

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-https:

virtual-router \*<vr> forwarding-instance \*<instance> protocols https
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


.. py:function:: make_protocols_https(None)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols https` node

    :param None: virtual-router \*<vr> forwarding-instance \*<instance> protocols

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp:

virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


Contains:

+-------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                        | Required   | Multi   |
+=============================================================================================================+============+=========+
| :ref:`community<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community>` | No         | No      |
+-------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`trap<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap>`           | No         | No      |
+-------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community:

virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp community
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                  | Required   | Multi   |
+=======================================================================================================================+============+=========+
| :ref:`community<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community:

virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp community \*<community>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community>`
Required  Yes
Multiple  Yes
Default:  -
Name      community
========  ================================================================================================================


Contains:

+-------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                    | Required   | Multi   |
+=========================================================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community-level>` | Yes        | Yes     |
+-------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community-level:

virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp community \*<community> level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community>`
Required  Yes
Multiple  No
Default:  -
========  ==========================================================================================================================


Contains:

+-------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                          | Required   | Multi   |
+===============================================================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community-level-level>` | Yes        | No      |
+-------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community-level-level:

virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp community \*<community> level <level>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-community-community-level>`
Required  Yes
Multiple  No
Default:  -
Name      level
========  ================================================================================================================================


.. py:function:: make_snmp_community_level(level)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp community \*<community> level <level>` node

    :param level: virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp community \*<community> level

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap:

virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp trap
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                             | Required   | Multi   |
+==================================================================================================================+============+=========+
| :ref:`community<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community>` | Yes        | No      |
+------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community:

virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp trap community
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap>`
Required  Yes
Multiple  No
Default:  -
========  ===========================================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                       | Required   | Multi   |
+============================================================================================================================+============+=========+
| :ref:`community<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community>` | Yes        | No      |
+----------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community:

virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp trap community \*<community>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community>`
Required  Yes
Multiple  Yes
Default:  -
Name      community
========  =====================================================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                       | Required   | Multi   |
+============================================================================================================================+============+=========+
| :ref:`host<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community-host>` | Yes        | Yes     |
+----------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community-host:

virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp trap community \*<community> host
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community>`
Required  Yes
Multiple  No
Default:  -
========  ===============================================================================================================================


Contains:

+---------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                  | Required   | Multi   |
+=======================================================================================================================================+============+=========+
| :ref:`address<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community-host-address>` | Yes        | No      |
+---------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community-host-address:

virtual-router \*<vr> forwarding-instance \*<instance> protocols snmp trap community \*<community> host \*<address>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-snmp-trap-community-community-host>`
Required  Yes
Multiple  Yes
Default:  -
Name      address
========  ====================================================================================================================================

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis:

virtual-router \*<vr> forwarding-instance \*<instance> protocols isis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


Contains:

+-------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                        | Required   | Multi   |
+=============================================================================================================+============+=========+
| :ref:`area<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-area>`           | No         | No      |
+-------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface>` | No         | No      |
+-------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-area:

virtual-router \*<vr> forwarding-instance \*<instance> protocols isis area
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                   | Required   | Multi   |
+========================================================================================================+============+=========+
| :ref:`area<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-area-area>` | Yes        | No      |
+--------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-area-area:

virtual-router \*<vr> forwarding-instance \*<instance> protocols isis area \*<area>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-area>`
Required  Yes
Multiple  Yes
Default:  -
Name      area
========  ===========================================================================================================


.. py:function:: make_isis_area(area)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols isis area \*<area>` node

    :param area: virtual-router \*<vr> forwarding-instance \*<instance> protocols isis area

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols isis interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                  | Required   | Multi   |
+=======================================================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols isis interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface>`
Required  Yes
Multiple  Yes
Default:  -
Name      interface
========  ================================================================================================================


.. py:function:: make_isis_interface(interface)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols isis interface \*<interface>` node

    :param interface: virtual-router \*<vr> forwarding-instance \*<instance> protocols isis interface


Contains:

+-------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                    | Required   | Multi   |
+=========================================================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface-level>` | No         | Yes     |
+-------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface-level:

virtual-router \*<vr> forwarding-instance \*<instance> protocols isis interface \*<interface> level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface>`
Required  No
Multiple  No
Default:  -
========  ==========================================================================================================================


Contains:

+-------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                          | Required   | Multi   |
+===============================================================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface-level-level>` | Yes        | No      |
+-------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface-level-level:

virtual-router \*<vr> forwarding-instance \*<instance> protocols isis interface \*<interface> level \*<level>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-isis-interface-interface-level>`
Required  Yes
Multiple  Yes
Default:  -
Name      level
========  ================================================================================================================================


.. py:function:: make_isis_level(level)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols isis interface \*<interface> level \*<level>` node

    :param level: virtual-router \*<vr> forwarding-instance \*<instance> protocols isis interface \*<interface> level

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf:

virtual-router \*<vr> forwarding-instance \*<instance> protocols ospf
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


Contains:

+-------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                        | Required   | Multi   |
+=============================================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf-interface>` | No         | No      |
+-------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols ospf interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                  | Required   | Multi   |
+=======================================================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf-interface-interface>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf-interface-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols ospf interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ospf-interface>`
Required  Yes
Multiple  Yes
Default:  -
Name      interface
========  ================================================================================================================


.. py:function:: make_ospf_interface(interface)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols ospf interface \*<interface>` node

    :param interface: virtual-router \*<vr> forwarding-instance \*<instance> protocols ospf interface

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp:

virtual-router \*<vr> forwarding-instance \*<instance> protocols ldp
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                       | Required   | Multi   |
+============================================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp-interface>` | No         | No      |
+------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols ldp interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp>`
Required  No
Multiple  No
Default:  -
========  =====================================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                 | Required   | Multi   |
+======================================================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp-interface-interface>` | Yes        | No      |
+----------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp-interface-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols ldp interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-ldp-interface>`
Required  Yes
Multiple  Yes
Default:  -
Name      interface
========  ===============================================================================================================


.. py:function:: make_ldp_interface(interface)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols ldp interface \*<interface>` node

    :param interface: virtual-router \*<vr> forwarding-instance \*<instance> protocols ldp interface

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp:

virtual-router \*<vr> forwarding-instance \*<instance> protocols rsvp
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


Contains:

+-------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                        | Required   | Multi   |
+=============================================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp-interface>` | No         | No      |
+-------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols rsvp interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp>`
Required  No
Multiple  No
Default:  -
========  ======================================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                  | Required   | Multi   |
+=======================================================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp-interface-interface>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp-interface-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols rsvp interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-rsvp-interface>`
Required  Yes
Multiple  Yes
Default:  -
Name      interface
========  ================================================================================================================


.. py:function:: make_rsvp_interface(interface)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols rsvp interface \*<interface>` node

    :param interface: virtual-router \*<vr> forwarding-instance \*<instance> protocols rsvp interface

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim:

virtual-router \*<vr> forwarding-instance \*<instance> protocols pim
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                       | Required   | Multi   |
+============================================================================================================+============+=========+
| :ref:`mode<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-mode>`           | Yes        | No      |
+------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-interface>` | No         | No      |
+------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-mode:

virtual-router \*<vr> forwarding-instance \*<instance> protocols pim mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim>`
Required  Yes
Multiple  No
Default:  -
========  =====================================================================================================


Contains:

+-------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                  | Required   | Multi   |
+=======================================================================================================+============+=========+
| :ref:`mode<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-mode-mode>` | Yes        | No      |
+-------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-mode-mode:

virtual-router \*<vr> forwarding-instance \*<instance> protocols pim mode <mode>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-mode>`
Required  Yes
Multiple  No
Default:  -
Name      mode
========  ==========================================================================================================


.. py:function:: make_pim_mode(mode)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols pim mode <mode>` node

    :param mode: virtual-router \*<vr> forwarding-instance \*<instance> protocols pim mode

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols pim interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim>`
Required  No
Multiple  No
Default:  -
========  =====================================================================================================


Contains:

+----------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                 | Required   | Multi   |
+======================================================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-interface-interface>` | Yes        | No      |
+----------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-interface-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols pim interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-pim-interface>`
Required  Yes
Multiple  Yes
Default:  -
Name      interface
========  ===============================================================================================================


.. py:function:: make_pim_interface(interface)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols pim interface \*<interface>` node

    :param interface: virtual-router \*<vr> forwarding-instance \*<instance> protocols pim interface

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping:

virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols>`
Required  No
Multiple  No
Default:  -
========  =================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                       | Required   | Multi   |
+============================================================================================================+============+=========+
| :ref:`vlan<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan>` | No         | No      |
+------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan:

virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                            | Required   | Multi   |
+=================================================================================================================+============+=========+
| :ref:`vlan<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan>` | No         | No      |
+-----------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan:

virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan>`
Required  No
Multiple  Yes
Default:  -
Name      vlan
========  ====================================================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                       | Required   | Multi   |
+============================================================================================================================================+============+=========+
| :ref:`version<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-version>`                 | No         | Yes     |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`immediate-leave<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-immediate-leave>` | No         | Yes     |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface>`             | No         | Yes     |
+--------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-version:

virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan> version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan>`
Required  No
Multiple  No
Default:  -
========  =========================================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                               | Required   | Multi   |
+====================================================================================================================================+============+=========+
| :ref:`version<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-version-version>` | Yes        | No      |
+------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-version-version:

virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan> version <version>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-version>`
Required  Yes
Multiple  No
Default:  -
Name      version
========  =================================================================================================================================

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-immediate-leave:

virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan> immediate-leave
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan>`
Required  No
Multiple  No
Default:  -
========  =========================================================================================================================

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan> interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan>`
Required  No
Multiple  No
Default:  -
========  =========================================================================================================================


Contains:

+------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                     | Required   | Multi   |
+==========================================================================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface-interface>` | No         | No      |
+------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface-interface:

virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan> interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  ===================================================================================================================================


.. py:function:: make_igmp_snooping_interface(interface)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan> interface \*<interface>` node

    :param interface: virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan> interface


Contains:

+------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                                                             | Required   | Multi   |
+==================================================================================================================================================================+============+=========+
| :ref:`multicast-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface-interface-multicast-router>` | No         | Yes     |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface-interface-multicast-router:

virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan> interface \*<interface> multicast-router
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================================================================
Parent    :ref:`virtual-router<dev-confdb-syntax-virtual-router-vr-forwarding-instance-instance-protocols-igmp-snooping-vlan-vlan-interface-interface>`
Required  No
Multiple  No
Default:  -
========  =============================================================================================================================================


.. py:function:: make_igmp_snooping_multicast_router(None)

    Generate `virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan> interface \*<interface> multicast-router` node

    :param None: virtual-router \*<vr> forwarding-instance \*<instance> protocols igmp-snooping vlan \*<vlan> interface \*<interface>

