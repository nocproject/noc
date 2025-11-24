.. _dev-confdb-syntax-interfaces:

interfaces
^^^^^^^^^^

========  ==
Parent    -
Required  No
Multiple  No
Default:  -
========  ==


Contains:

+----------------------------------------------------------+------------+---------+
| Node                                                     | Required   | Multi   |
+==========================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-interfaces-interface>` | No         | No      |
+----------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface:

interfaces \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  ===============================================


.. py:function:: make_interface(interface)

    Generate `interfaces \*<interface>` node

    :param interface: interfaces


Contains:

+----------------------------------------------------------------------------+------------+---------+
| Node                                                                       | Required   | Multi   |
+============================================================================+============+=========+
| :ref:`meta<dev-confdb-syntax-interfaces-interface-meta>`                   | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`type<dev-confdb-syntax-interfaces-interface-type>`                   | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`description<dev-confdb-syntax-interfaces-interface-description>`     | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`admin-status<dev-confdb-syntax-interfaces-interface-admin-status>`   | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`mtu<dev-confdb-syntax-interfaces-interface-mtu>`                     | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`speed<dev-confdb-syntax-interfaces-interface-speed>`                 | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`duplex<dev-confdb-syntax-interfaces-interface-duplex>`               | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`flow-control<dev-confdb-syntax-interfaces-interface-flow-control>`   | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`ethernet<dev-confdb-syntax-interfaces-interface-ethernet>`           | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`storm-control<dev-confdb-syntax-interfaces-interface-storm-control>` | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta:

interfaces \*<interface> meta
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+---------------------------------------------------------------------+------------+---------+
| Node                                                                | Required   | Multi   |
+=====================================================================+============+=========+
| :ref:`profile<dev-confdb-syntax-interfaces-interface-meta-profile>` | No         | No      |
+---------------------------------------------------------------------+------------+---------+
| :ref:`link<dev-confdb-syntax-interfaces-interface-meta-link>`       | No         | No      |
+---------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-profile:

interfaces \*<interface> meta profile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta>`
Required  No
Multiple  No
Default:  -
========  ==============================================================


Contains:

+-----------------------------------------------------------------------+------------+---------+
| Node                                                                  | Required   | Multi   |
+=======================================================================+============+=========+
| :ref:`id<dev-confdb-syntax-interfaces-interface-meta-profile-id>`     | No         | No      |
+-----------------------------------------------------------------------+------------+---------+
| :ref:`name<dev-confdb-syntax-interfaces-interface-meta-profile-name>` | No         | No      |
+-----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-profile-id:

interfaces \*<interface> meta profile id
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-profile>`
Required  No
Multiple  No
Default:  -
========  ======================================================================


Contains:

+----------------------------------------------------------------------+------------+---------+
| Node                                                                 | Required   | Multi   |
+======================================================================+============+=========+
| :ref:`id<dev-confdb-syntax-interfaces-interface-meta-profile-id-id>` | Yes        | No      |
+----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-profile-id-id:

interfaces \*<interface> meta profile id <id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-profile-id>`
Required  Yes
Multiple  No
Default:  -
Name      id
========  =========================================================================


.. py:function:: make_interfaces_meta_profile_id(id)

    Generate `interfaces \*<interface> meta profile id <id>` node

    :param id: interfaces \*<interface> meta profile id

.. _dev-confdb-syntax-interfaces-interface-meta-profile-name:

interfaces \*<interface> meta profile name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-profile>`
Required  No
Multiple  No
Default:  -
========  ======================================================================


Contains:

+----------------------------------------------------------------------------+------------+---------+
| Node                                                                       | Required   | Multi   |
+============================================================================+============+=========+
| :ref:`name<dev-confdb-syntax-interfaces-interface-meta-profile-name-name>` | Yes        | No      |
+----------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-profile-name-name:

interfaces \*<interface> meta profile name <name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-profile-name>`
Required  Yes
Multiple  No
Default:  -
Name      name
========  ===========================================================================


.. py:function:: make_interfaces_meta_profile_name(name)

    Generate `interfaces \*<interface> meta profile name <name>` node

    :param name: interfaces \*<interface> meta profile name

.. _dev-confdb-syntax-interfaces-interface-meta-link:

interfaces \*<interface> meta link
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta>`
Required  No
Multiple  No
Default:  -
========  ==============================================================


Contains:

+--------------------------------------------------------------------+------------+---------+
| Node                                                               | Required   | Multi   |
+====================================================================+============+=========+
| :ref:`link<dev-confdb-syntax-interfaces-interface-meta-link-link>` | No         | No      |
+--------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-link-link:

interfaces \*<interface> meta link \*<link>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link>`
Required  No
Multiple  Yes
Default:  -
Name      link
========  ===================================================================


Contains:

+-----------------------------------------------------------------------------------+------------+---------+
| Node                                                                              | Required   | Multi   |
+===================================================================================+============+=========+
| :ref:`object<dev-confdb-syntax-interfaces-interface-meta-link-link-object>`       | No         | Yes     |
+-----------------------------------------------------------------------------------+------------+---------+
| :ref:`interface<dev-confdb-syntax-interfaces-interface-meta-link-link-interface>` | No         | Yes     |
+-----------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object:

interfaces \*<interface> meta link \*<link> object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link>`
Required  No
Multiple  No
Default:  -
========  ========================================================================


Contains:

+--------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                 | Required   | Multi   |
+======================================================================================+============+=========+
| :ref:`id<dev-confdb-syntax-interfaces-interface-meta-link-link-object-id>`           | No         | No      |
+--------------------------------------------------------------------------------------+------------+---------+
| :ref:`name<dev-confdb-syntax-interfaces-interface-meta-link-link-object-name>`       | No         | No      |
+--------------------------------------------------------------------------------------+------------+---------+
| :ref:`profile<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile>` | No         | No      |
+--------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-id:

interfaces \*<interface> meta link \*<link> object id
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+---------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                        | Required   | Multi   |
+=============================================================================================+============+=========+
| :ref:`object_id<dev-confdb-syntax-interfaces-interface-meta-link-link-object-id-object_id>` | Yes        | No      |
+---------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-id-object_id:

interfaces \*<interface> meta link \*<link> object id <object_id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object-id>`
Required  Yes
Multiple  No
Default:  -
Name      object_id
========  ==================================================================================


.. py:function:: make_interfaces_meta_link_object_id(object_id)

    Generate `interfaces \*<interface> meta link \*<link> object id <object_id>` node

    :param object_id: interfaces \*<interface> meta link \*<link> object id

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-name:

interfaces \*<interface> meta link \*<link> object name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+---------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                              | Required   | Multi   |
+===================================================================================================+============+=========+
| :ref:`object_name<dev-confdb-syntax-interfaces-interface-meta-link-link-object-name-object_name>` | Yes        | No      |
+---------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-name-object_name:

interfaces \*<interface> meta link \*<link> object name <object_name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object-name>`
Required  Yes
Multiple  No
Default:  -
Name      object_name
========  ====================================================================================


.. py:function:: make_interfaces_meta_link_object_name(object_name)

    Generate `interfaces \*<interface> meta link \*<link> object name <object_name>` node

    :param object_name: interfaces \*<interface> meta link \*<link> object name

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile:

interfaces \*<interface> meta link \*<link> object profile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                     | Required   | Multi   |
+==========================================================================================+============+=========+
| :ref:`id<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-id>`       | No         | No      |
+------------------------------------------------------------------------------------------+------------+---------+
| :ref:`name<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-name>`   | No         | No      |
+------------------------------------------------------------------------------------------+------------+---------+
| :ref:`level<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-level>` | No         | No      |
+------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-id:

interfaces \*<interface> meta link \*<link> object profile id
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+---------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                  | Required   | Multi   |
+=======================================================================================+============+=========+
| :ref:`id<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-id-id>` | Yes        | No      |
+---------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-id-id:

interfaces \*<interface> meta link \*<link> object profile id <id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-id>`
Required  Yes
Multiple  No
Default:  -
Name      id
========  ==========================================================================================


.. py:function:: make_interfaces_meta_link_object_profile_id(id)

    Generate `interfaces \*<interface> meta link \*<link> object profile id <id>` node

    :param id: interfaces \*<interface> meta link \*<link> object profile id

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-name:

interfaces \*<interface> meta link \*<link> object profile name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+---------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                        | Required   | Multi   |
+=============================================================================================+============+=========+
| :ref:`name<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-name-name>` | Yes        | No      |
+---------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-name-name:

interfaces \*<interface> meta link \*<link> object profile name <name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-name>`
Required  Yes
Multiple  No
Default:  -
Name      name
========  ============================================================================================


.. py:function:: make_interfaces_meta_link_object_profile_name(name)

    Generate `interfaces \*<interface> meta link \*<link> object profile name <name>` node

    :param name: interfaces \*<interface> meta link \*<link> object profile name

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-level:

interfaces \*<interface> meta link \*<link> object profile level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                           | Required   | Multi   |
+================================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-level-level>` | Yes        | No      |
+------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-level-level:

interfaces \*<interface> meta link \*<link> object profile level <level>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-object-profile-level>`
Required  Yes
Multiple  No
Default:  -
Name      level
========  =============================================================================================


.. py:function:: make_interfaces_meta_link_object_profile_level(level)

    Generate `interfaces \*<interface> meta link \*<link> object profile level <level>` node

    :param level: interfaces \*<interface> meta link \*<link> object profile level

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-interface:

interfaces \*<interface> meta link \*<link> interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link>`
Required  No
Multiple  No
Default:  -
========  ========================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                      | Required   | Multi   |
+===========================================================================================================+============+=========+
| :ref:`remote_interface<dev-confdb-syntax-interfaces-interface-meta-link-link-interface-remote_interface>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-meta-link-link-interface-remote_interface:

interfaces \*<interface> meta link \*<link> interface \*<remote_interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-meta-link-link-interface>`
Required  Yes
Multiple  Yes
Default:  -
Name      remote_interface
========  ==================================================================================


.. py:function:: make_interfaces_meta_link_interface(remote_interface)

    Generate `interfaces \*<interface> meta link \*<link> interface \*<remote_interface>` node

    :param remote_interface: interfaces \*<interface> meta link \*<link> interface

.. _dev-confdb-syntax-interfaces-interface-type:

interfaces \*<interface> type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+---------------------------------------------------------------+------------+---------+
| Node                                                          | Required   | Multi   |
+===============================================================+============+=========+
| :ref:`type<dev-confdb-syntax-interfaces-interface-type-type>` | Yes        | No      |
+---------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-type-type:

interfaces \*<interface> type <type>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-type>`
Required  Yes
Multiple  No
Default:  -
Name      type
========  ==============================================================


.. py:function:: make_interface_type(type)

    Generate `interfaces \*<interface> type <type>` node

    :param type: interfaces \*<interface> type

.. _dev-confdb-syntax-interfaces-interface-description:

interfaces \*<interface> description
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+------------------------------------------------------------------------------------+------------+---------+
| Node                                                                               | Required   | Multi   |
+====================================================================================+============+=========+
| :ref:`description<dev-confdb-syntax-interfaces-interface-description-description>` | Yes        | No      |
+------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-description-description:

interfaces \*<interface> description <description>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-description>`
Required  Yes
Multiple  No
Default:  -
Name      description
========  =====================================================================


.. py:function:: make_interface_description(description)

    Generate `interfaces \*<interface> description <description>` node

    :param description: interfaces \*<interface> description

.. _dev-confdb-syntax-interfaces-interface-admin-status:

interfaces \*<interface> admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+---------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                  | Required   | Multi   |
+=======================================================================================+============+=========+
| :ref:`admin_status<dev-confdb-syntax-interfaces-interface-admin-status-admin_status>` | Yes        | No      |
+---------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-admin-status-admin_status:

interfaces \*<interface> admin-status <admin_status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-admin-status>`
Required  Yes
Multiple  No
Default:  -
Name      admin_status
========  ======================================================================


.. py:function:: make_interface_admin_status(admin_status)

    Generate `interfaces \*<interface> admin-status <admin_status>` node

    :param admin_status: interfaces \*<interface> admin-status

.. _dev-confdb-syntax-interfaces-interface-mtu:

interfaces \*<interface> mtu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+------------------------------------------------------------+------------+---------+
| Node                                                       | Required   | Multi   |
+============================================================+============+=========+
| :ref:`mtu<dev-confdb-syntax-interfaces-interface-mtu-mtu>` | Yes        | No      |
+------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-mtu-mtu:

interfaces \*<interface> mtu <mtu>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-mtu>`
Required  Yes
Multiple  No
Default:  -
Name      mtu
========  =============================================================


.. py:function:: make_interface_mtu(mtu)

    Generate `interfaces \*<interface> mtu <mtu>` node

    :param mtu: interfaces \*<interface> mtu

.. _dev-confdb-syntax-interfaces-interface-speed:

interfaces \*<interface> speed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+------------------------------------------------------------------+------------+---------+
| Node                                                             | Required   | Multi   |
+==================================================================+============+=========+
| :ref:`speed<dev-confdb-syntax-interfaces-interface-speed-speed>` | Yes        | No      |
+------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-speed-speed:

interfaces \*<interface> speed <speed>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-speed>`
Required  Yes
Multiple  No
Default:  -
Name      speed
========  ===============================================================


.. py:function:: make_interface_speed(speed)

    Generate `interfaces \*<interface> speed <speed>` node

    :param speed: interfaces \*<interface> speed

.. _dev-confdb-syntax-interfaces-interface-duplex:

interfaces \*<interface> duplex
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+---------------------------------------------------------------------+------------+---------+
| Node                                                                | Required   | Multi   |
+=====================================================================+============+=========+
| :ref:`duplex<dev-confdb-syntax-interfaces-interface-duplex-duplex>` | Yes        | No      |
+---------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-duplex-duplex:

interfaces \*<interface> duplex <duplex>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-duplex>`
Required  Yes
Multiple  No
Default:  -
Name      duplex
========  ================================================================


.. py:function:: make_interface_duplex(duplex)

    Generate `interfaces \*<interface> duplex <duplex>` node

    :param duplex: interfaces \*<interface> duplex

.. _dev-confdb-syntax-interfaces-interface-flow-control:

interfaces \*<interface> flow-control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+---------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                  | Required   | Multi   |
+=======================================================================================+============+=========+
| :ref:`flow_control<dev-confdb-syntax-interfaces-interface-flow-control-flow_control>` | Yes        | No      |
+---------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-flow-control-flow_control:

interfaces \*<interface> flow-control <flow_control>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-flow-control>`
Required  Yes
Multiple  No
Default:  -
Name      flow_control
========  ======================================================================


.. py:function:: make_interface_flow_control(flow_control)

    Generate `interfaces \*<interface> flow-control <flow_control>` node

    :param flow_control: interfaces \*<interface> flow-control

.. _dev-confdb-syntax-interfaces-interface-ethernet:

interfaces \*<interface> ethernet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+-------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                      | Required   | Multi   |
+===========================================================================================+============+=========+
| :ref:`auto-negotiation<dev-confdb-syntax-interfaces-interface-ethernet-auto-negotiation>` | No         | No      |
+-------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-ethernet-auto-negotiation:

interfaces \*<interface> ethernet auto-negotiation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-ethernet>`
Required  No
Multiple  No
Default:  -
========  ==================================================================


Contains:

+------------------------------------------------------------------------------------+------------+---------+
| Node                                                                               | Required   | Multi   |
+====================================================================================+============+=========+
| :ref:`mode<dev-confdb-syntax-interfaces-interface-ethernet-auto-negotiation-mode>` | No         | No      |
+------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-ethernet-auto-negotiation-mode:

interfaces \*<interface> ethernet auto-negotiation \*<mode>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-ethernet-auto-negotiation>`
Required  No
Multiple  Yes
Default:  -
Name      mode
========  ===================================================================================


.. py:function:: make_interface_ethernet_autonegotiation(mode)

    Generate `interfaces \*<interface> ethernet auto-negotiation \*<mode>` node

    :param mode: interfaces \*<interface> ethernet auto-negotiation

.. _dev-confdb-syntax-interfaces-interface-storm-control:

interfaces \*<interface> storm-control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+----------------------------------------------------------------------------------+------------+---------+
| Node                                                                             | Required   | Multi   |
+==================================================================================+============+=========+
| :ref:`broadcast<dev-confdb-syntax-interfaces-interface-storm-control-broadcast>` | No         | No      |
+----------------------------------------------------------------------------------+------------+---------+
| :ref:`multicast<dev-confdb-syntax-interfaces-interface-storm-control-multicast>` | No         | No      |
+----------------------------------------------------------------------------------+------------+---------+
| :ref:`unicast<dev-confdb-syntax-interfaces-interface-storm-control-unicast>`     | No         | No      |
+----------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-storm-control-broadcast:

interfaces \*<interface> storm-control broadcast
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-storm-control>`
Required  No
Multiple  No
Default:  -
========  =======================================================================


Contains:

+------------------------------------------------------------------------------------+------------+---------+
| Node                                                                               | Required   | Multi   |
+====================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-interfaces-interface-storm-control-broadcast-level>` | No         | No      |
+------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-storm-control-broadcast-level:

interfaces \*<interface> storm-control broadcast level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-storm-control-broadcast>`
Required  No
Multiple  No
Default:  -
========  =================================================================================


Contains:

+------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                     | Required   | Multi   |
+==========================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-interfaces-interface-storm-control-broadcast-level-level>` | Yes        | No      |
+------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-storm-control-broadcast-level-level:

interfaces \*<interface> storm-control broadcast level <level>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-storm-control-broadcast-level>`
Required  Yes
Multiple  No
Default:  -
Name      level
========  =======================================================================================


.. py:function:: make_interface_storm_control_broadcast_level(level)

    Generate `interfaces \*<interface> storm-control broadcast level <level>` node

    :param level: interfaces \*<interface> storm-control broadcast level

.. _dev-confdb-syntax-interfaces-interface-storm-control-multicast:

interfaces \*<interface> storm-control multicast
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-storm-control>`
Required  No
Multiple  No
Default:  -
========  =======================================================================


Contains:

+------------------------------------------------------------------------------------+------------+---------+
| Node                                                                               | Required   | Multi   |
+====================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-interfaces-interface-storm-control-multicast-level>` | No         | No      |
+------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-storm-control-multicast-level:

interfaces \*<interface> storm-control multicast level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-storm-control-multicast>`
Required  No
Multiple  No
Default:  -
========  =================================================================================


Contains:

+------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                     | Required   | Multi   |
+==========================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-interfaces-interface-storm-control-multicast-level-level>` | Yes        | No      |
+------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-storm-control-multicast-level-level:

interfaces \*<interface> storm-control multicast level <level>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-storm-control-multicast-level>`
Required  Yes
Multiple  No
Default:  -
Name      level
========  =======================================================================================


.. py:function:: make_interface_storm_control_multicast_level(level)

    Generate `interfaces \*<interface> storm-control multicast level <level>` node

    :param level: interfaces \*<interface> storm-control multicast level

.. _dev-confdb-syntax-interfaces-interface-storm-control-unicast:

interfaces \*<interface> storm-control unicast
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-storm-control>`
Required  No
Multiple  No
Default:  -
========  =======================================================================


Contains:

+----------------------------------------------------------------------------------+------------+---------+
| Node                                                                             | Required   | Multi   |
+==================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-interfaces-interface-storm-control-unicast-level>` | No         | No      |
+----------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-storm-control-unicast-level:

interfaces \*<interface> storm-control unicast level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-storm-control-unicast>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+----------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                   | Required   | Multi   |
+========================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-interfaces-interface-storm-control-unicast-level-level>` | Yes        | No      |
+----------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-interfaces-interface-storm-control-unicast-level-level:

interfaces \*<interface> storm-control unicast level <level>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================================
Parent    :ref:`interfaces<dev-confdb-syntax-interfaces-interface-storm-control-unicast-level>`
Required  Yes
Multiple  No
Default:  -
Name      level
========  =====================================================================================


.. py:function:: make_interface_storm_control_unicast_level(level)

    Generate `interfaces \*<interface> storm-control unicast level <level>` node

    :param level: interfaces \*<interface> storm-control unicast level

