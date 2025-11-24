.. _dev-confdb-syntax-hints:

hints
^^^^^

========  ==
Parent    -
Required  No
Multiple  No
Default:  -
========  ==


Contains:

+-------------------------------------------------------+------------+---------+
| Node                                                  | Required   | Multi   |
+=======================================================+============+=========+
| :ref:`interfaces<dev-confdb-syntax-hints-interfaces>` | No         | No      |
+-------------------------------------------------------+------------+---------+
| :ref:`protocols<dev-confdb-syntax-hints-protocols>`   | No         | No      |
+-------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-interfaces:

hints interfaces
^^^^^^^^^^^^^^^^

========  =====================================
Parent    :ref:`hints<dev-confdb-syntax-hints>`
Required  No
Multiple  No
Default:  -
========  =====================================


Contains:

+--------------------------------------------------------------+------------+---------+
| Node                                                         | Required   | Multi   |
+==============================================================+============+=========+
| :ref:`defaults<dev-confdb-syntax-hints-interfaces-defaults>` | No         | No      |
+--------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-interfaces-defaults:

hints interfaces defaults
^^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-interfaces>`
Required  No
Multiple  No
Default:  -
========  ================================================


Contains:

+-------------------------------------------------------------------------------+------------+---------+
| Node                                                                          | Required   | Multi   |
+===============================================================================+============+=========+
| :ref:`admin-status<dev-confdb-syntax-hints-interfaces-defaults-admin-status>` | No         | No      |
+-------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-interfaces-defaults-admin-status:

hints interfaces defaults admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-interfaces-defaults>`
Required  No
Multiple  No
Default:  -
========  =========================================================


Contains:

+--------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                       | Required   | Multi   |
+============================================================================================+============+=========+
| :ref:`admin_status<dev-confdb-syntax-hints-interfaces-defaults-admin-status-admin_status>` | Yes        | No      |
+--------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-interfaces-defaults-admin-status-admin_status:

hints interfaces defaults admin-status <admin_status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-interfaces-defaults-admin-status>`
Required  Yes
Multiple  No
Default:  -
Name      admin_status
========  ======================================================================


.. py:function:: make_defaults_interface_admin_status(admin_status)

    Generate `hints interfaces defaults admin-status <admin_status>` node

    :param admin_status: hints interfaces defaults admin-status

.. _dev-confdb-syntax-hints-protocols:

hints protocols
^^^^^^^^^^^^^^^

========  =====================================
Parent    :ref:`hints<dev-confdb-syntax-hints>`
Required  No
Multiple  No
Default:  -
========  =====================================


Contains:

+-----------------------------------------------------------------------+------------+---------+
| Node                                                                  | Required   | Multi   |
+=======================================================================+============+=========+
| :ref:`lldp<dev-confdb-syntax-hints-protocols-lldp>`                   | No         | No      |
+-----------------------------------------------------------------------+------------+---------+
| :ref:`cdp<dev-confdb-syntax-hints-protocols-cdp>`                     | No         | No      |
+-----------------------------------------------------------------------+------------+---------+
| :ref:`spanning-tree<dev-confdb-syntax-hints-protocols-spanning-tree>` | No         | No      |
+-----------------------------------------------------------------------+------------+---------+
| :ref:`loop-detect<dev-confdb-syntax-hints-protocols-loop-detect>`     | No         | No      |
+-----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-lldp:

hints protocols lldp
^^^^^^^^^^^^^^^^^^^^

========  ===============================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols>`
Required  No
Multiple  No
Default:  -
========  ===============================================


Contains:

+--------------------------------------------------------------------+------------+---------+
| Node                                                               | Required   | Multi   |
+====================================================================+============+=========+
| :ref:`status<dev-confdb-syntax-hints-protocols-lldp-status>`       | No         | No      |
+--------------------------------------------------------------------+------------+---------+
| :ref:`interface<dev-confdb-syntax-hints-protocols-lldp-interface>` | No         | No      |
+--------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-lldp-status:

hints protocols lldp status
^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-lldp>`
Required  No
Multiple  No
Default:  -
========  ====================================================


Contains:

+---------------------------------------------------------------------+------------+---------+
| Node                                                                | Required   | Multi   |
+=====================================================================+============+=========+
| :ref:`status<dev-confdb-syntax-hints-protocols-lldp-status-status>` | Yes        | No      |
+---------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-lldp-status-status:

hints protocols lldp status <status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-lldp-status>`
Required  Yes
Multiple  No
Default:  -
Name      status
========  ===========================================================


.. py:function:: make_global_lldp_status(status)

    Generate `hints protocols lldp status <status>` node

    :param status: hints protocols lldp status

.. _dev-confdb-syntax-hints-protocols-lldp-interface:

hints protocols lldp interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-lldp>`
Required  No
Multiple  No
Default:  -
========  ====================================================


Contains:

+------------------------------------------------------------------------------+------------+---------+
| Node                                                                         | Required   | Multi   |
+==============================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-hints-protocols-lldp-interface-interface>` | No         | No      |
+------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-lldp-interface-interface:

hints protocols lldp interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-lldp-interface>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  ==============================================================


Contains:

+----------------------------------------------------------------------------+------------+---------+
| Node                                                                       | Required   | Multi   |
+============================================================================+============+=========+
| :ref:`off<dev-confdb-syntax-hints-protocols-lldp-interface-interface-off>` | No         | Yes     |
+----------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-lldp-interface-interface-off:

hints protocols lldp interface \*<interface> off
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-lldp-interface-interface>`
Required  No
Multiple  No
Default:  -
========  ========================================================================


.. py:function:: make_lldp_interface_disable(None)

    Generate `hints protocols lldp interface \*<interface> off` node

    :param None: hints protocols lldp interface \*<interface>

.. _dev-confdb-syntax-hints-protocols-cdp:

hints protocols cdp
^^^^^^^^^^^^^^^^^^^

========  ===============================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols>`
Required  No
Multiple  No
Default:  -
========  ===============================================


Contains:

+-------------------------------------------------------------------+------------+---------+
| Node                                                              | Required   | Multi   |
+===================================================================+============+=========+
| :ref:`status<dev-confdb-syntax-hints-protocols-cdp-status>`       | No         | No      |
+-------------------------------------------------------------------+------------+---------+
| :ref:`interface<dev-confdb-syntax-hints-protocols-cdp-interface>` | No         | No      |
+-------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-cdp-status:

hints protocols cdp status
^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-cdp>`
Required  No
Multiple  No
Default:  -
========  ===================================================


Contains:

+--------------------------------------------------------------------+------------+---------+
| Node                                                               | Required   | Multi   |
+====================================================================+============+=========+
| :ref:`status<dev-confdb-syntax-hints-protocols-cdp-status-status>` | Yes        | No      |
+--------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-cdp-status-status:

hints protocols cdp status <status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-cdp-status>`
Required  Yes
Multiple  No
Default:  -
Name      status
========  ==========================================================


.. py:function:: make_global_cdp_status(status)

    Generate `hints protocols cdp status <status>` node

    :param status: hints protocols cdp status

.. _dev-confdb-syntax-hints-protocols-cdp-interface:

hints protocols cdp interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-cdp>`
Required  No
Multiple  No
Default:  -
========  ===================================================


Contains:

+-----------------------------------------------------------------------------+------------+---------+
| Node                                                                        | Required   | Multi   |
+=============================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-hints-protocols-cdp-interface-interface>` | No         | No      |
+-----------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-cdp-interface-interface:

hints protocols cdp interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-cdp-interface>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  =============================================================


Contains:

+---------------------------------------------------------------------------+------------+---------+
| Node                                                                      | Required   | Multi   |
+===========================================================================+============+=========+
| :ref:`off<dev-confdb-syntax-hints-protocols-cdp-interface-interface-off>` | No         | Yes     |
+---------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-cdp-interface-interface-off:

hints protocols cdp interface \*<interface> off
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-cdp-interface-interface>`
Required  No
Multiple  No
Default:  -
========  =======================================================================


.. py:function:: make_cdp_interface_disable(None)

    Generate `hints protocols cdp interface \*<interface> off` node

    :param None: hints protocols cdp interface \*<interface>

.. _dev-confdb-syntax-hints-protocols-spanning-tree:

hints protocols spanning-tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols>`
Required  No
Multiple  No
Default:  -
========  ===============================================


Contains:

+-----------------------------------------------------------------------------+------------+---------+
| Node                                                                        | Required   | Multi   |
+=============================================================================+============+=========+
| :ref:`status<dev-confdb-syntax-hints-protocols-spanning-tree-status>`       | No         | No      |
+-----------------------------------------------------------------------------+------------+---------+
| :ref:`priority<dev-confdb-syntax-hints-protocols-spanning-tree-priority>`   | No         | No      |
+-----------------------------------------------------------------------------+------------+---------+
| :ref:`interface<dev-confdb-syntax-hints-protocols-spanning-tree-interface>` | No         | No      |
+-----------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-spanning-tree-status:

hints protocols spanning-tree status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-spanning-tree>`
Required  No
Multiple  No
Default:  -
========  =============================================================


Contains:

+------------------------------------------------------------------------------+------------+---------+
| Node                                                                         | Required   | Multi   |
+==============================================================================+============+=========+
| :ref:`status<dev-confdb-syntax-hints-protocols-spanning-tree-status-status>` | Yes        | No      |
+------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-spanning-tree-status-status:

hints protocols spanning-tree status <status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-spanning-tree-status>`
Required  Yes
Multiple  No
Default:  -
Name      status
========  ====================================================================


.. py:function:: make_global_spanning_tree_status(status)

    Generate `hints protocols spanning-tree status <status>` node

    :param status: hints protocols spanning-tree status

.. _dev-confdb-syntax-hints-protocols-spanning-tree-priority:

hints protocols spanning-tree priority
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-spanning-tree>`
Required  No
Multiple  No
Default:  -
========  =============================================================


Contains:

+------------------------------------------------------------------------------------+------------+---------+
| Node                                                                               | Required   | Multi   |
+====================================================================================+============+=========+
| :ref:`priority<dev-confdb-syntax-hints-protocols-spanning-tree-priority-priority>` | Yes        | No      |
+------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-spanning-tree-priority-priority:

hints protocols spanning-tree priority <priority>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-spanning-tree-priority>`
Required  Yes
Multiple  No
Default:  -
Name      priority
========  ======================================================================


.. py:function:: make_global_spanning_tree_priority(priority)

    Generate `hints protocols spanning-tree priority <priority>` node

    :param priority: hints protocols spanning-tree priority

.. _dev-confdb-syntax-hints-protocols-spanning-tree-interface:

hints protocols spanning-tree interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =============================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-spanning-tree>`
Required  No
Multiple  No
Default:  -
========  =============================================================


Contains:

+---------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                  | Required   | Multi   |
+=======================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-hints-protocols-spanning-tree-interface-interface>` | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-spanning-tree-interface-interface:

hints protocols spanning-tree interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-spanning-tree-interface>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  =======================================================================


Contains:

+-------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                | Required   | Multi   |
+=====================================================================================+============+=========+
| :ref:`off<dev-confdb-syntax-hints-protocols-spanning-tree-interface-interface-off>` | No         | Yes     |
+-------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-spanning-tree-interface-interface-off:

hints protocols spanning-tree interface \*<interface> off
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-spanning-tree-interface-interface>`
Required  No
Multiple  No
Default:  -
========  =================================================================================


.. py:function:: make_spanning_tree_interface_disable(None)

    Generate `hints protocols spanning-tree interface \*<interface> off` node

    :param None: hints protocols spanning-tree interface \*<interface>

.. _dev-confdb-syntax-hints-protocols-loop-detect:

hints protocols loop-detect
^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols>`
Required  No
Multiple  No
Default:  -
========  ===============================================


Contains:

+---------------------------------------------------------------------------+------------+---------+
| Node                                                                      | Required   | Multi   |
+===========================================================================+============+=========+
| :ref:`status<dev-confdb-syntax-hints-protocols-loop-detect-status>`       | No         | No      |
+---------------------------------------------------------------------------+------------+---------+
| :ref:`interface<dev-confdb-syntax-hints-protocols-loop-detect-interface>` | No         | No      |
+---------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-loop-detect-status:

hints protocols loop-detect status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-loop-detect>`
Required  No
Multiple  No
Default:  -
========  ===========================================================


Contains:

+----------------------------------------------------------------------------+------------+---------+
| Node                                                                       | Required   | Multi   |
+============================================================================+============+=========+
| :ref:`status<dev-confdb-syntax-hints-protocols-loop-detect-status-status>` | Yes        | No      |
+----------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-loop-detect-status-status:

hints protocols loop-detect status <status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-loop-detect-status>`
Required  Yes
Multiple  No
Default:  -
Name      status
========  ==================================================================


.. py:function:: make_global_loop_detect_status(status)

    Generate `hints protocols loop-detect status <status>` node

    :param status: hints protocols loop-detect status

.. _dev-confdb-syntax-hints-protocols-loop-detect-interface:

hints protocols loop-detect interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-loop-detect>`
Required  No
Multiple  No
Default:  -
========  ===========================================================


Contains:

+-------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                | Required   | Multi   |
+=====================================================================================+============+=========+
| :ref:`interface<dev-confdb-syntax-hints-protocols-loop-detect-interface-interface>` | No         | No      |
+-------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-loop-detect-interface-interface:

hints protocols loop-detect interface \*<interface>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-loop-detect-interface>`
Required  No
Multiple  Yes
Default:  -
Name      interface
========  =====================================================================


Contains:

+-----------------------------------------------------------------------------------+------------+---------+
| Node                                                                              | Required   | Multi   |
+===================================================================================+============+=========+
| :ref:`off<dev-confdb-syntax-hints-protocols-loop-detect-interface-interface-off>` | No         | Yes     |
+-----------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-hints-protocols-loop-detect-interface-interface-off:

hints protocols loop-detect interface \*<interface> off
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`hints<dev-confdb-syntax-hints-protocols-loop-detect-interface-interface>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


.. py:function:: make_loop_detect_interface_disable(None)

    Generate `hints protocols loop-detect interface \*<interface> off` node

    :param None: hints protocols loop-detect interface \*<interface>

