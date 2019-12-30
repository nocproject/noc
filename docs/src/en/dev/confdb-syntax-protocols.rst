.. _dev-confdb-syntax-protocols:

protocols
^^^^^^^^^

========  ==
Parent    -
Required  No
Multiple  No
Default:  -
========  ==


Contains:

+-----------------------------------------------------------------+------------+---------+
| Node                                                            | Required   | Multi   |
+=================================================================+============+=========+
| :ref:`ntp<dev-confdb-syntax-protocols-ntp>`                     | No         | No      |
+-----------------------------------------------------------------+------------+---------+
| :ref:`cdp<dev-confdb-syntax-protocols-cdp>`                     | No         | No      |
+-----------------------------------------------------------------+------------+---------+
| :ref:`lldp<dev-confdb-syntax-protocols-lldp>`                   | No         | No      |
+-----------------------------------------------------------------+------------+---------+
| :ref:`udld<dev-confdb-syntax-protocols-udld>`                   | No         | No      |
+-----------------------------------------------------------------+------------+---------+
| :ref:`spanning-tree<dev-confdb-syntax-protocols-spanning-tree>` | No         | No      |
+-----------------------------------------------------------------+------------+---------+
| :ref:`loop-detect<dev-confdb-syntax-protocols-loop-detect>`     | No         | No      |
+-----------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp:

protocols ntp
^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols>`
Required  No
Multiple  No
Default:  -
========  =============================================


Contains:

+-----------------------------------------------------------------+------------+---------+
| Node                                                            | Required   | Multi   |
+=================================================================+============+=========+
| :ref:`name<dev-confdb-syntax-protocols-ntp-name>`               | No         | No      |
+-----------------------------------------------------------------+------------+---------+
| :ref:`boot-server<dev-confdb-syntax-protocols-ntp-boot-server>` | No         | No      |
+-----------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name:

protocols ntp \*<name>
^^^^^^^^^^^^^^^^^^^^^^

========  =================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp>`
Required  No
Multiple  Yes
Default:  -
Name      name
========  =================================================


.. py:function:: make_ntp_server(name)

    Generate `protocols ntp \*<name>` node

    :param name: protocols ntp


Contains:

+----------------------------------------------------------------------------+------------+---------+
| Node                                                                       | Required   | Multi   |
+============================================================================+============+=========+
| :ref:`version<dev-confdb-syntax-protocols-ntp-name-version>`               | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`address<dev-confdb-syntax-protocols-ntp-name-address>`               | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`mode<dev-confdb-syntax-protocols-ntp-name-mode>`                     | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`authentication<dev-confdb-syntax-protocols-ntp-name-authentication>` | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`prefer<dev-confdb-syntax-protocols-ntp-name-prefer>`                 | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+
| :ref:`broadcast<dev-confdb-syntax-protocols-ntp-name-broadcast>`           | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-version:

protocols ntp \*<name> version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name>`
Required  No
Multiple  No
Default:  -
========  ======================================================


Contains:

+----------------------------------------------------------------------+------------+---------+
| Node                                                                 | Required   | Multi   |
+======================================================================+============+=========+
| :ref:`version<dev-confdb-syntax-protocols-ntp-name-version-version>` | Yes        | No      |
+----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-version-version:

protocols ntp \*<name> version <version>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-version>`
Required  Yes
Multiple  No
Default:  -
Name      version
========  ==============================================================


.. py:function:: make_ntp_server_version(version)

    Generate `protocols ntp \*<name> version <version>` node

    :param version: protocols ntp \*<name> version

.. _dev-confdb-syntax-protocols-ntp-name-address:

protocols ntp \*<name> address
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name>`
Required  No
Multiple  No
Default:  -
========  ======================================================


Contains:

+----------------------------------------------------------------------+------------+---------+
| Node                                                                 | Required   | Multi   |
+======================================================================+============+=========+
| :ref:`address<dev-confdb-syntax-protocols-ntp-name-address-address>` | Yes        | No      |
+----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-address-address:

protocols ntp \*<name> address <address>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-address>`
Required  Yes
Multiple  No
Default:  -
Name      address
========  ==============================================================


.. py:function:: make_ntp_server_address(address)

    Generate `protocols ntp \*<name> address <address>` node

    :param address: protocols ntp \*<name> address

.. _dev-confdb-syntax-protocols-ntp-name-mode:

protocols ntp \*<name> mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name>`
Required  No
Multiple  No
Default:  -
========  ======================================================


Contains:

+-------------------------------------------------------------+------------+---------+
| Node                                                        | Required   | Multi   |
+=============================================================+============+=========+
| :ref:`mode<dev-confdb-syntax-protocols-ntp-name-mode-mode>` | Yes        | No      |
+-------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-mode-mode:

protocols ntp \*<name> mode <mode>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-mode>`
Required  Yes
Multiple  No
Default:  -
Name      mode
========  ===========================================================


.. py:function:: make_ntp_server_mode(mode)

    Generate `protocols ntp \*<name> mode <mode>` node

    :param mode: protocols ntp \*<name> mode

.. _dev-confdb-syntax-protocols-ntp-name-authentication:

protocols ntp \*<name> authentication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name>`
Required  No
Multiple  No
Default:  -
========  ======================================================


Contains:

+-----------------------------------------------------------------------+------------+---------+
| Node                                                                  | Required   | Multi   |
+=======================================================================+============+=========+
| :ref:`type<dev-confdb-syntax-protocols-ntp-name-authentication-type>` | No         | No      |
+-----------------------------------------------------------------------+------------+---------+
| :ref:`key<dev-confdb-syntax-protocols-ntp-name-authentication-key>`   | No         | No      |
+-----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-authentication-type:

protocols ntp \*<name> authentication type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-authentication>`
Required  No
Multiple  No
Default:  -
========  =====================================================================


Contains:

+--------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                 | Required   | Multi   |
+======================================================================================+============+=========+
| :ref:`auth_type<dev-confdb-syntax-protocols-ntp-name-authentication-type-auth_type>` | Yes        | No      |
+--------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-authentication-type-auth_type:

protocols ntp \*<name> authentication type <auth_type>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-authentication-type>`
Required  Yes
Multiple  No
Default:  -
Name      auth_type
========  ==========================================================================


.. py:function:: make_ntp_server_authentication_type(auth_type)

    Generate `protocols ntp \*<name> authentication type <auth_type>` node

    :param auth_type: protocols ntp \*<name> authentication type

.. _dev-confdb-syntax-protocols-ntp-name-authentication-key:

protocols ntp \*<name> authentication key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-authentication>`
Required  No
Multiple  No
Default:  -
========  =====================================================================


Contains:

+-------------------------------------------------------------------------+------------+---------+
| Node                                                                    | Required   | Multi   |
+=========================================================================+============+=========+
| :ref:`key<dev-confdb-syntax-protocols-ntp-name-authentication-key-key>` | Yes        | No      |
+-------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-authentication-key-key:

protocols ntp \*<name> authentication key <key>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-authentication-key>`
Required  Yes
Multiple  No
Default:  -
Name      key
========  =========================================================================


.. py:function:: make_ntp_server_authentication_key(key)

    Generate `protocols ntp \*<name> authentication key <key>` node

    :param key: protocols ntp \*<name> authentication key

.. _dev-confdb-syntax-protocols-ntp-name-prefer:

protocols ntp \*<name> prefer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name>`
Required  No
Multiple  No
Default:  -
========  ======================================================


.. py:function:: make_ntp_server_prefer(None)

    Generate `protocols ntp \*<name> prefer` node

    :param None: protocols ntp \*<name>

.. _dev-confdb-syntax-protocols-ntp-name-broadcast:

protocols ntp \*<name> broadcast
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name>`
Required  No
Multiple  No
Default:  -
========  ======================================================


Contains:

+--------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                 | Required   | Multi   |
+======================================================================================+============+=========+
| :ref:`version<dev-confdb-syntax-protocols-ntp-name-broadcast-version>`               | No         | No      |
+--------------------------------------------------------------------------------------+------------+---------+
| :ref:`address<dev-confdb-syntax-protocols-ntp-name-broadcast-address>`               | No         | No      |
+--------------------------------------------------------------------------------------+------------+---------+
| :ref:`ttl<dev-confdb-syntax-protocols-ntp-name-broadcast-ttl>`                       | No         | No      |
+--------------------------------------------------------------------------------------+------------+---------+
| :ref:`authentication<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication>` | No         | No      |
+--------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-version:

protocols ntp \*<name> broadcast version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast>`
Required  No
Multiple  No
Default:  -
========  ================================================================


Contains:

+--------------------------------------------------------------------------------+------------+---------+
| Node                                                                           | Required   | Multi   |
+================================================================================+============+=========+
| :ref:`version<dev-confdb-syntax-protocols-ntp-name-broadcast-version-version>` | Yes        | No      |
+--------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-version-version:

protocols ntp \*<name> broadcast version <version>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast-version>`
Required  Yes
Multiple  No
Default:  -
Name      version
========  ========================================================================


.. py:function:: make_ntp_server_broadcast_version(version)

    Generate `protocols ntp \*<name> broadcast version <version>` node

    :param version: protocols ntp \*<name> broadcast version

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-address:

protocols ntp \*<name> broadcast address
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast>`
Required  No
Multiple  No
Default:  -
========  ================================================================


Contains:

+--------------------------------------------------------------------------------+------------+---------+
| Node                                                                           | Required   | Multi   |
+================================================================================+============+=========+
| :ref:`address<dev-confdb-syntax-protocols-ntp-name-broadcast-address-address>` | Yes        | No      |
+--------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-address-address:

protocols ntp \*<name> broadcast address <address>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast-address>`
Required  Yes
Multiple  No
Default:  -
Name      address
========  ========================================================================


.. py:function:: make_ntp_server_broadcast_address(address)

    Generate `protocols ntp \*<name> broadcast address <address>` node

    :param address: protocols ntp \*<name> broadcast address

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-ttl:

protocols ntp \*<name> broadcast ttl
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast>`
Required  No
Multiple  No
Default:  -
========  ================================================================


Contains:

+--------------------------------------------------------------------+------------+---------+
| Node                                                               | Required   | Multi   |
+====================================================================+============+=========+
| :ref:`ttl<dev-confdb-syntax-protocols-ntp-name-broadcast-ttl-ttl>` | Yes        | No      |
+--------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-ttl-ttl:

protocols ntp \*<name> broadcast ttl <ttl>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast-ttl>`
Required  Yes
Multiple  No
Default:  -
Name      ttl
========  ====================================================================


.. py:function:: make_ntp_server_broadcast_ttl(ttl)

    Generate `protocols ntp \*<name> broadcast ttl <ttl>` node

    :param ttl: protocols ntp \*<name> broadcast ttl

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-authentication:

protocols ntp \*<name> broadcast authentication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast>`
Required  No
Multiple  No
Default:  -
========  ================================================================


Contains:

+---------------------------------------------------------------------------------+------------+---------+
| Node                                                                            | Required   | Multi   |
+=================================================================================+============+=========+
| :ref:`type<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-type>` | No         | No      |
+---------------------------------------------------------------------------------+------------+---------+
| :ref:`key<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-key>`   | No         | No      |
+---------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-type:

protocols ntp \*<name> broadcast authentication type
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                           | Required   | Multi   |
+================================================================================================+============+=========+
| :ref:`auth_type<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-type-auth_type>` | Yes        | No      |
+------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-type-auth_type:

protocols ntp \*<name> broadcast authentication type <auth_type>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-type>`
Required  Yes
Multiple  No
Default:  -
Name      auth_type
========  ====================================================================================


.. py:function:: make_ntp_server_broadcast_authentication_type(auth_type)

    Generate `protocols ntp \*<name> broadcast authentication type <auth_type>` node

    :param auth_type: protocols ntp \*<name> broadcast authentication type

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-key:

protocols ntp \*<name> broadcast authentication key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+-----------------------------------------------------------------------------------+------------+---------+
| Node                                                                              | Required   | Multi   |
+===================================================================================+============+=========+
| :ref:`key<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-key-key>` | Yes        | No      |
+-----------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-key-key:

protocols ntp \*<name> broadcast authentication key <key>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-name-broadcast-authentication-key>`
Required  Yes
Multiple  No
Default:  -
Name      key
========  ===================================================================================


.. py:function:: make_ntp_server_broadcast_authentication_key(key)

    Generate `protocols ntp \*<name> broadcast authentication key <key>` node

    :param key: protocols ntp \*<name> broadcast authentication key

.. _dev-confdb-syntax-protocols-ntp-boot-server:

protocols ntp boot-server
^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp>`
Required  No
Multiple  No
Default:  -
========  =================================================


Contains:

+-----------------------------------------------------------------------------+------------+---------+
| Node                                                                        | Required   | Multi   |
+=============================================================================+============+=========+
| :ref:`boot_server<dev-confdb-syntax-protocols-ntp-boot-server-boot_server>` | No         | No      |
+-----------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-ntp-boot-server-boot_server:

protocols ntp boot-server <boot_server>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-ntp-boot-server>`
Required  No
Multiple  No
Default:  -
Name      boot_server
========  =============================================================


.. py:function:: make_ntp_boot_server(boot_server)

    Generate `protocols ntp boot-server <boot_server>` node

    :param boot_server: protocols ntp boot-server

.. _dev-confdb-syntax-protocols-cdp:

protocols cdp
^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols>`
Required  No
Multiple  No
Default:  -
========  =============================================


Contains:

+-------------------------------------------------------------+------------+---------+
| Node                                                        | Required   | Multi   |
+=============================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-protocols-cdp-interface>` | No         | No      |
+-------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-cdp-interface:

protocols cdp interface
^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-cdp>`
Required  No
Multiple  No
Default:  -
========  =================================================


Contains:

+-----------------------------------------------------------------------+------------+---------+
| Node                                                                  | Required   | Multi   |
+=======================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-protocols-cdp-interface-interface>` | No         | No      |
+-----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-cdp-interface-interface:

protocols cdp interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-cdp-interface>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  ===========================================================


.. py:function:: make_cdp_interface(interface)

    Generate `protocols cdp interface \*<interface>` node

    :param interface: protocols cdp interface

.. _dev-confdb-syntax-protocols-lldp:

protocols lldp
^^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols>`
Required  No
Multiple  No
Default:  -
========  =============================================


Contains:

+--------------------------------------------------------------+------------+---------+
| Node                                                         | Required   | Multi   |
+==============================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-protocols-lldp-interface>` | No         | No      |
+--------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-lldp-interface:

protocols lldp interface
^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-lldp>`
Required  No
Multiple  No
Default:  -
========  ==================================================


Contains:

+------------------------------------------------------------------------+------------+---------+
| Node                                                                   | Required   | Multi   |
+========================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-protocols-lldp-interface-interface>` | No         | No      |
+------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-lldp-interface-interface:

protocols lldp interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-lldp-interface>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  ============================================================


.. py:function:: make_lldp_interface(interface)

    Generate `protocols lldp interface \*<interface>` node

    :param interface: protocols lldp interface


Contains:

+----------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                   | Required   | Multi   |
+========================================================================================+============+=========+
| :ref:`admin-status<dev-confdb-syntax-protocols-lldp-interface-interface-admin-status>` | No         | Yes     |
+----------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-lldp-interface-interface-admin-status:

protocols lldp interface \*<interface> admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-lldp-interface-interface>`
Required  No
Multiple  No
Default:  -
========  ======================================================================


Contains:

+---------------------------------------------------------------------------------+------------+---------+
| Node                                                                            | Required   | Multi   |
+=================================================================================+============+=========+
| :ref:`rx<dev-confdb-syntax-protocols-lldp-interface-interface-admin-status-rx>` | No         | No      |
+---------------------------------------------------------------------------------+------------+---------+
| :ref:`tx<dev-confdb-syntax-protocols-lldp-interface-interface-admin-status-tx>` | No         | No      |
+---------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-lldp-interface-interface-admin-status-rx:

protocols lldp interface \*<interface> admin-status rx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-lldp-interface-interface-admin-status>`
Required  No
Multiple  No
Default:  -
========  ===================================================================================


.. py:function:: make_lldp_admin_status_rx(None)

    Generate `protocols lldp interface \*<interface> admin-status rx` node

    :param None: protocols lldp interface \*<interface> admin-status

.. _dev-confdb-syntax-protocols-lldp-interface-interface-admin-status-tx:

protocols lldp interface \*<interface> admin-status tx
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-lldp-interface-interface-admin-status>`
Required  No
Multiple  No
Default:  -
========  ===================================================================================


.. py:function:: make_lldp_admin_status_tx(None)

    Generate `protocols lldp interface \*<interface> admin-status tx` node

    :param None: protocols lldp interface \*<interface> admin-status

.. _dev-confdb-syntax-protocols-udld:

protocols udld
^^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols>`
Required  No
Multiple  No
Default:  -
========  =============================================


Contains:

+--------------------------------------------------------------+------------+---------+
| Node                                                         | Required   | Multi   |
+==============================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-protocols-udld-interface>` | No         | No      |
+--------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-udld-interface:

protocols udld interface
^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-udld>`
Required  No
Multiple  No
Default:  -
========  ==================================================


Contains:

+------------------------------------------------------------------------+------------+---------+
| Node                                                                   | Required   | Multi   |
+========================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-protocols-udld-interface-interface>` | No         | No      |
+------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-udld-interface-interface:

protocols udld interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-udld-interface>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  ============================================================


.. py:function:: make_udld_interface(interface)

    Generate `protocols udld interface \*<interface>` node

    :param interface: protocols udld interface

.. _dev-confdb-syntax-protocols-spanning-tree:

protocols spanning-tree
^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols>`
Required  No
Multiple  No
Default:  -
========  =============================================


Contains:

+-----------------------------------------------------------------------+------------+---------+
| Node                                                                  | Required   | Multi   |
+=======================================================================+============+=========+
| :ref:`mode<dev-confdb-syntax-protocols-spanning-tree-mode>`           | No         | No      |
+-----------------------------------------------------------------------+------------+---------+
| :ref:`priority<dev-confdb-syntax-protocols-spanning-tree-priority>`   | No         | No      |
+-----------------------------------------------------------------------+------------+---------+
| :ref:`instance<dev-confdb-syntax-protocols-spanning-tree-instance>`   | No         | No      |
+-----------------------------------------------------------------------+------------+---------+
| :ref:`interface<dev-confdb-syntax-protocols-spanning-tree-interface>` | No         | No      |
+-----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-mode:

protocols spanning-tree mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree>`
Required  No
Multiple  No
Default:  -
========  ===========================================================


Contains:

+------------------------------------------------------------------+------------+---------+
| Node                                                             | Required   | Multi   |
+==================================================================+============+=========+
| :ref:`mode<dev-confdb-syntax-protocols-spanning-tree-mode-mode>` | Yes        | No      |
+------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-mode-mode:

protocols spanning-tree mode <mode>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-mode>`
Required  Yes
Multiple  No
Default:  -
Name      mode
========  ================================================================


.. py:function:: make_spanning_tree_mode(mode)

    Generate `protocols spanning-tree mode <mode>` node

    :param mode: protocols spanning-tree mode

.. _dev-confdb-syntax-protocols-spanning-tree-priority:

protocols spanning-tree priority
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree>`
Required  No
Multiple  No
Default:  -
========  ===========================================================


Contains:

+------------------------------------------------------------------------------+------------+---------+
| Node                                                                         | Required   | Multi   |
+==============================================================================+============+=========+
| :ref:`priority<dev-confdb-syntax-protocols-spanning-tree-priority-priority>` | Yes        | No      |
+------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-priority-priority:

protocols spanning-tree priority <priority>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-priority>`
Required  Yes
Multiple  No
Default:  -
Name      priority
========  ====================================================================


.. py:function:: make_spanning_tree_priority(priority)

    Generate `protocols spanning-tree priority <priority>` node

    :param priority: protocols spanning-tree priority

.. _dev-confdb-syntax-protocols-spanning-tree-instance:

protocols spanning-tree instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree>`
Required  No
Multiple  No
Default:  -
========  ===========================================================


Contains:

+------------------------------------------------------------------------------+------------+---------+
| Node                                                                         | Required   | Multi   |
+==============================================================================+============+=========+
| :ref:`instance<dev-confdb-syntax-protocols-spanning-tree-instance-instance>` | No         | No      |
+------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-instance-instance:

protocols spanning-tree instance \*<instance>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-instance>`
Required  No
Multiple  Yes
Default:  0
Name      instance
========  ====================================================================


Contains:

+-----------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                | Required   | Multi   |
+=====================================================================================================+============+=========+
| :ref:`bridge-priority<dev-confdb-syntax-protocols-spanning-tree-instance-instance-bridge-priority>` | No         | Yes     |
+-----------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-instance-instance-bridge-priority:

protocols spanning-tree instance \*<instance> bridge-priority
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-instance-instance>`
Required  No
Multiple  No
Default:  -
========  =============================================================================


Contains:

+-------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                  | Required   | Multi   |
+=======================================================================================================+============+=========+
| :ref:`priority<dev-confdb-syntax-protocols-spanning-tree-instance-instance-bridge-priority-priority>` | Yes        | No      |
+-------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-instance-instance-bridge-priority-priority:

protocols spanning-tree instance \*<instance> bridge-priority <priority>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-instance-instance-bridge-priority>`
Required  Yes
Multiple  No
Default:  -
Name      priority
========  =============================================================================================


.. py:function:: make_spanning_tree_instance_bridge_priority(priority)

    Generate `protocols spanning-tree instance \*<instance> bridge-priority <priority>` node

    :param priority: protocols spanning-tree instance \*<instance> bridge-priority

.. _dev-confdb-syntax-protocols-spanning-tree-interface:

protocols spanning-tree interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree>`
Required  No
Multiple  No
Default:  -
========  ===========================================================


Contains:

+---------------------------------------------------------------------------------+------------+---------+
| Node                                                                            | Required   | Multi   |
+=================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-protocols-spanning-tree-interface-interface>` | No         | No      |
+---------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface:

protocols spanning-tree interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  =====================================================================


Contains:

+-------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                            | Required   | Multi   |
+=================================================================================================+============+=========+
| :ref:`admin-status<dev-confdb-syntax-protocols-spanning-tree-interface-interface-admin-status>` | No         | Yes     |
+-------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`cost<dev-confdb-syntax-protocols-spanning-tree-interface-interface-cost>`                 | No         | Yes     |
+-------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`bpdu-filter<dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-filter>`   | No         | Yes     |
+-------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`bpdu-guard<dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-guard>`     | No         | Yes     |
+-------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`mode<dev-confdb-syntax-protocols-spanning-tree-interface-interface-mode>`                 | No         | Yes     |
+-------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface-admin-status:

protocols spanning-tree interface \*<interface> admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface-interface>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                         | Required   | Multi   |
+==============================================================================================================+============+=========+
| :ref:`admin_status<dev-confdb-syntax-protocols-spanning-tree-interface-interface-admin-status-admin_status>` | Yes        | No      |
+--------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface-admin-status-admin_status:

protocols spanning-tree interface \*<interface> admin-status <admin_status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface-interface-admin-status>`
Required  Yes
Multiple  No
Default:  -
Name      admin_status
========  ============================================================================================


.. py:function:: make_interface_spanning_tree_admin_status(admin_status)

    Generate `protocols spanning-tree interface \*<interface> admin-status <admin_status>` node

    :param admin_status: protocols spanning-tree interface \*<interface> admin-status

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface-cost:

protocols spanning-tree interface \*<interface> cost
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface-interface>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+--------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                 | Required   | Multi   |
+======================================================================================+============+=========+
| :ref:`cost<dev-confdb-syntax-protocols-spanning-tree-interface-interface-cost-cost>` | Yes        | No      |
+--------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface-cost-cost:

protocols spanning-tree interface \*<interface> cost <cost>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface-interface-cost>`
Required  Yes
Multiple  No
Default:  -
Name      cost
========  ====================================================================================


.. py:function:: make_spanning_tree_interface_cost(cost)

    Generate `protocols spanning-tree interface \*<interface> cost <cost>` node

    :param cost: protocols spanning-tree interface \*<interface> cost

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-filter:

protocols spanning-tree interface \*<interface> bpdu-filter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface-interface>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+---------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                              | Required   | Multi   |
+===================================================================================================+============+=========+
| :ref:`enabled<dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-filter-enabled>` | Yes        | No      |
+---------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-filter-enabled:

protocols spanning-tree interface \*<interface> bpdu-filter <enabled>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-filter>`
Required  Yes
Multiple  No
Default:  -
Name      enabled
========  ===========================================================================================


.. py:function:: make_spanning_tree_interface_bpdu_filter(enabled)

    Generate `protocols spanning-tree interface \*<interface> bpdu-filter <enabled>` node

    :param enabled: protocols spanning-tree interface \*<interface> bpdu-filter

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-guard:

protocols spanning-tree interface \*<interface> bpdu-guard
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface-interface>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+--------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                             | Required   | Multi   |
+==================================================================================================+============+=========+
| :ref:`enabled<dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-guard-enabled>` | Yes        | No      |
+--------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-guard-enabled:

protocols spanning-tree interface \*<interface> bpdu-guard <enabled>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface-interface-bpdu-guard>`
Required  Yes
Multiple  No
Default:  -
Name      enabled
========  ==========================================================================================


.. py:function:: make_spanning_tree_interface_bpdu_guard(enabled)

    Generate `protocols spanning-tree interface \*<interface> bpdu-guard <enabled>` node

    :param enabled: protocols spanning-tree interface \*<interface> bpdu-guard

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface-mode:

protocols spanning-tree interface \*<interface> mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface-interface>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+--------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                 | Required   | Multi   |
+======================================================================================+============+=========+
| :ref:`mode<dev-confdb-syntax-protocols-spanning-tree-interface-interface-mode-mode>` | Yes        | No      |
+--------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-spanning-tree-interface-interface-mode-mode:

protocols spanning-tree interface \*<interface> mode <mode>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-spanning-tree-interface-interface-mode>`
Required  Yes
Multiple  No
Default:  -
Name      mode
========  ====================================================================================


.. py:function:: make_spanning_tree_interface_mode(mode)

    Generate `protocols spanning-tree interface \*<interface> mode <mode>` node

    :param mode: protocols spanning-tree interface \*<interface> mode

.. _dev-confdb-syntax-protocols-loop-detect:

protocols loop-detect
^^^^^^^^^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols>`
Required  No
Multiple  No
Default:  -
========  =============================================


Contains:

+---------------------------------------------------------------------+------------+---------+
| Node                                                                | Required   | Multi   |
+=====================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-protocols-loop-detect-interface>` | No         | No      |
+---------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-loop-detect-interface:

protocols loop-detect interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-loop-detect>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+-------------------------------------------------------------------------------+------------+---------+
| Node                                                                          | Required   | Multi   |
+===============================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-protocols-loop-detect-interface-interface>` | No         | No      |
+-------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-protocols-loop-detect-interface-interface:

protocols loop-detect interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================
Parent    :ref:`protocols<dev-confdb-syntax-protocols-loop-detect-interface>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  ===================================================================


.. py:function:: make_loop_detect_interface(interface)

    Generate `protocols loop-detect interface \*<interface>` node

    :param interface: protocols loop-detect interface

