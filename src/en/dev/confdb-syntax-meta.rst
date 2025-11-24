.. _dev-confdb-syntax-meta:

meta
^^^^

========  ==
Parent    -
Required  No
Multiple  No
Default:  -
========  ==


Contains:

+--------------------------------------------------------------+------------+---------+
| Node                                                         | Required   | Multi   |
+==============================================================+============+=========+
| :ref:`id<dev-confdb-syntax-meta-id>`                         | No         | No      |
+--------------------------------------------------------------+------------+---------+
| :ref:`profile<dev-confdb-syntax-meta-profile>`               | No         | No      |
+--------------------------------------------------------------+------------+---------+
| :ref:`vendor<dev-confdb-syntax-meta-vendor>`                 | No         | No      |
+--------------------------------------------------------------+------------+---------+
| :ref:`platform<dev-confdb-syntax-meta-platform>`             | No         | No      |
+--------------------------------------------------------------+------------+---------+
| :ref:`version<dev-confdb-syntax-meta-version>`               | No         | No      |
+--------------------------------------------------------------+------------+---------+
| :ref:`object-profile<dev-confdb-syntax-meta-object-profile>` | No         | No      |
+--------------------------------------------------------------+------------+---------+
| :ref:`segment<dev-confdb-syntax-meta-segment>`               | No         | No      |
+--------------------------------------------------------------+------------+---------+
| :ref:`management<dev-confdb-syntax-meta-management>`         | No         | No      |
+--------------------------------------------------------------+------------+---------+
| :ref:`tags<dev-confdb-syntax-meta-tags>`                     | No         | No      |
+--------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-id:

meta id
^^^^^^^

========  ===================================
Parent    :ref:`meta<dev-confdb-syntax-meta>`
Required  No
Multiple  No
Default:  -
========  ===================================


Contains:

+-----------------------------------------+------------+---------+
| Node                                    | Required   | Multi   |
+=========================================+============+=========+
| :ref:`id<dev-confdb-syntax-meta-id-id>` | Yes        | No      |
+-----------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-id-id:

meta id <id>
^^^^^^^^^^^^

========  ======================================
Parent    :ref:`meta<dev-confdb-syntax-meta-id>`
Required  Yes
Multiple  No
Default:  -
Name      id
========  ======================================


.. py:function:: make_meta_id(id)

    Generate `meta id <id>` node

    :param id: meta id

.. _dev-confdb-syntax-meta-profile:

meta profile
^^^^^^^^^^^^

========  ===================================
Parent    :ref:`meta<dev-confdb-syntax-meta>`
Required  No
Multiple  No
Default:  -
========  ===================================


Contains:

+--------------------------------------------------------+------------+---------+
| Node                                                   | Required   | Multi   |
+========================================================+============+=========+
| :ref:`profile<dev-confdb-syntax-meta-profile-profile>` | Yes        | No      |
+--------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-profile-profile:

meta profile <profile>
^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================
Parent    :ref:`meta<dev-confdb-syntax-meta-profile>`
Required  Yes
Multiple  No
Default:  -
Name      profile
========  ===========================================


.. py:function:: make_meta_profile(profile)

    Generate `meta profile <profile>` node

    :param profile: meta profile

.. _dev-confdb-syntax-meta-vendor:

meta vendor
^^^^^^^^^^^

========  ===================================
Parent    :ref:`meta<dev-confdb-syntax-meta>`
Required  No
Multiple  No
Default:  -
========  ===================================


Contains:

+-----------------------------------------------------+------------+---------+
| Node                                                | Required   | Multi   |
+=====================================================+============+=========+
| :ref:`vendor<dev-confdb-syntax-meta-vendor-vendor>` | Yes        | No      |
+-----------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-vendor-vendor:

meta vendor <vendor>
^^^^^^^^^^^^^^^^^^^^

========  ==========================================
Parent    :ref:`meta<dev-confdb-syntax-meta-vendor>`
Required  Yes
Multiple  No
Default:  -
Name      vendor
========  ==========================================


.. py:function:: make_meta_vendor(vendor)

    Generate `meta vendor <vendor>` node

    :param vendor: meta vendor

.. _dev-confdb-syntax-meta-platform:

meta platform
^^^^^^^^^^^^^

========  ===================================
Parent    :ref:`meta<dev-confdb-syntax-meta>`
Required  No
Multiple  No
Default:  -
========  ===================================


Contains:

+-----------------------------------------------------------+------------+---------+
| Node                                                      | Required   | Multi   |
+===========================================================+============+=========+
| :ref:`platform<dev-confdb-syntax-meta-platform-platform>` | Yes        | No      |
+-----------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-platform-platform:

meta platform <platform>
^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================
Parent    :ref:`meta<dev-confdb-syntax-meta-platform>`
Required  Yes
Multiple  No
Default:  -
Name      platform
========  ============================================


.. py:function:: make_meta_platform(platform)

    Generate `meta platform <platform>` node

    :param platform: meta platform

.. _dev-confdb-syntax-meta-version:

meta version
^^^^^^^^^^^^

========  ===================================
Parent    :ref:`meta<dev-confdb-syntax-meta>`
Required  No
Multiple  No
Default:  -
========  ===================================


Contains:

+--------------------------------------------------------+------------+---------+
| Node                                                   | Required   | Multi   |
+========================================================+============+=========+
| :ref:`version<dev-confdb-syntax-meta-version-version>` | Yes        | No      |
+--------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-version-version:

meta version <version>
^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================
Parent    :ref:`meta<dev-confdb-syntax-meta-version>`
Required  Yes
Multiple  No
Default:  -
Name      version
========  ===========================================


.. py:function:: make_meta_version(version)

    Generate `meta version <version>` node

    :param version: meta version

.. _dev-confdb-syntax-meta-object-profile:

meta object-profile
^^^^^^^^^^^^^^^^^^^

========  ===================================
Parent    :ref:`meta<dev-confdb-syntax-meta>`
Required  No
Multiple  No
Default:  -
========  ===================================


Contains:

+-----------------------------------------------------------+------------+---------+
| Node                                                      | Required   | Multi   |
+===========================================================+============+=========+
| :ref:`id<dev-confdb-syntax-meta-object-profile-id>`       | No         | No      |
+-----------------------------------------------------------+------------+---------+
| :ref:`name<dev-confdb-syntax-meta-object-profile-name>`   | No         | No      |
+-----------------------------------------------------------+------------+---------+
| :ref:`level<dev-confdb-syntax-meta-object-profile-level>` | No         | No      |
+-----------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-object-profile-id:

meta object-profile id
^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================
Parent    :ref:`meta<dev-confdb-syntax-meta-object-profile>`
Required  No
Multiple  No
Default:  -
========  ==================================================


Contains:

+--------------------------------------------------------+------------+---------+
| Node                                                   | Required   | Multi   |
+========================================================+============+=========+
| :ref:`id<dev-confdb-syntax-meta-object-profile-id-id>` | Yes        | No      |
+--------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-object-profile-id-id:

meta object-profile id <id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================
Parent    :ref:`meta<dev-confdb-syntax-meta-object-profile-id>`
Required  Yes
Multiple  No
Default:  -
Name      id
========  =====================================================


.. py:function:: make_meta_object_profile_id(id)

    Generate `meta object-profile id <id>` node

    :param id: meta object-profile id

.. _dev-confdb-syntax-meta-object-profile-name:

meta object-profile name
^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================
Parent    :ref:`meta<dev-confdb-syntax-meta-object-profile>`
Required  No
Multiple  No
Default:  -
========  ==================================================


Contains:

+--------------------------------------------------------------+------------+---------+
| Node                                                         | Required   | Multi   |
+==============================================================+============+=========+
| :ref:`name<dev-confdb-syntax-meta-object-profile-name-name>` | Yes        | No      |
+--------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-object-profile-name-name:

meta object-profile name <name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================
Parent    :ref:`meta<dev-confdb-syntax-meta-object-profile-name>`
Required  Yes
Multiple  No
Default:  -
Name      name
========  =======================================================


.. py:function:: make_meta_object_profile_name(name)

    Generate `meta object-profile name <name>` node

    :param name: meta object-profile name

.. _dev-confdb-syntax-meta-object-profile-level:

meta object-profile level
^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================
Parent    :ref:`meta<dev-confdb-syntax-meta-object-profile>`
Required  No
Multiple  No
Default:  -
========  ==================================================


Contains:

+-----------------------------------------------------------------+------------+---------+
| Node                                                            | Required   | Multi   |
+=================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-meta-object-profile-level-level>` | Yes        | No      |
+-----------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-object-profile-level-level:

meta object-profile level <level>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================
Parent    :ref:`meta<dev-confdb-syntax-meta-object-profile-level>`
Required  Yes
Multiple  No
Default:  -
Name      level
========  ========================================================


.. py:function:: make_meta_object_profile_level(level)

    Generate `meta object-profile level <level>` node

    :param level: meta object-profile level

.. _dev-confdb-syntax-meta-segment:

meta segment
^^^^^^^^^^^^

========  ===================================
Parent    :ref:`meta<dev-confdb-syntax-meta>`
Required  No
Multiple  No
Default:  -
========  ===================================


Contains:

+--------------------------------------------------+------------+---------+
| Node                                             | Required   | Multi   |
+==================================================+============+=========+
| :ref:`id<dev-confdb-syntax-meta-segment-id>`     | No         | No      |
+--------------------------------------------------+------------+---------+
| :ref:`name<dev-confdb-syntax-meta-segment-name>` | No         | No      |
+--------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-segment-id:

meta segment id
^^^^^^^^^^^^^^^

========  ===========================================
Parent    :ref:`meta<dev-confdb-syntax-meta-segment>`
Required  No
Multiple  No
Default:  -
========  ===========================================


Contains:

+-------------------------------------------------+------------+---------+
| Node                                            | Required   | Multi   |
+=================================================+============+=========+
| :ref:`id<dev-confdb-syntax-meta-segment-id-id>` | Yes        | No      |
+-------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-segment-id-id:

meta segment id <id>
^^^^^^^^^^^^^^^^^^^^

========  ==============================================
Parent    :ref:`meta<dev-confdb-syntax-meta-segment-id>`
Required  Yes
Multiple  No
Default:  -
Name      id
========  ==============================================


.. py:function:: make_meta_segment_id(id)

    Generate `meta segment id <id>` node

    :param id: meta segment id

.. _dev-confdb-syntax-meta-segment-name:

meta segment name
^^^^^^^^^^^^^^^^^

========  ===========================================
Parent    :ref:`meta<dev-confdb-syntax-meta-segment>`
Required  No
Multiple  No
Default:  -
========  ===========================================


Contains:

+-------------------------------------------------------+------------+---------+
| Node                                                  | Required   | Multi   |
+=======================================================+============+=========+
| :ref:`name<dev-confdb-syntax-meta-segment-name-name>` | Yes        | No      |
+-------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-segment-name-name:

meta segment name <name>
^^^^^^^^^^^^^^^^^^^^^^^^

========  ================================================
Parent    :ref:`meta<dev-confdb-syntax-meta-segment-name>`
Required  Yes
Multiple  No
Default:  -
Name      name
========  ================================================


.. py:function:: make_meta_segment_name(name)

    Generate `meta segment name <name>` node

    :param name: meta segment name

.. _dev-confdb-syntax-meta-management:

meta management
^^^^^^^^^^^^^^^

========  ===================================
Parent    :ref:`meta<dev-confdb-syntax-meta>`
Required  No
Multiple  No
Default:  -
========  ===================================


Contains:

+-------------------------------------------------------------+------------+---------+
| Node                                                        | Required   | Multi   |
+=============================================================+============+=========+
| :ref:`address<dev-confdb-syntax-meta-management-address>`   | No         | No      |
+-------------------------------------------------------------+------------+---------+
| :ref:`protocol<dev-confdb-syntax-meta-management-protocol>` | No         | No      |
+-------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-management-address:

meta management address
^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================
Parent    :ref:`meta<dev-confdb-syntax-meta-management>`
Required  No
Multiple  No
Default:  -
========  ==============================================


Contains:

+-------------------------------------------------------------------+------------+---------+
| Node                                                              | Required   | Multi   |
+===================================================================+============+=========+
| :ref:`address<dev-confdb-syntax-meta-management-address-address>` | Yes        | No      |
+-------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-management-address-address:

meta management address <address>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================
Parent    :ref:`meta<dev-confdb-syntax-meta-management-address>`
Required  Yes
Multiple  No
Default:  -
Name      address
========  ======================================================


.. py:function:: make_meta_management_address(address)

    Generate `meta management address <address>` node

    :param address: meta management address

.. _dev-confdb-syntax-meta-management-protocol:

meta management protocol
^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================
Parent    :ref:`meta<dev-confdb-syntax-meta-management>`
Required  No
Multiple  No
Default:  -
========  ==============================================


Contains:

+----------------------------------------------------------------------+------------+---------+
| Node                                                                 | Required   | Multi   |
+======================================================================+============+=========+
| :ref:`protocol<dev-confdb-syntax-meta-management-protocol-protocol>` | Yes        | No      |
+----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-management-protocol-protocol:

meta management protocol <protocol>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================
Parent    :ref:`meta<dev-confdb-syntax-meta-management-protocol>`
Required  Yes
Multiple  No
Default:  -
Name      protocol
========  =======================================================


.. py:function:: make_meta_management_protocol(protocol)

    Generate `meta management protocol <protocol>` node

    :param protocol: meta management protocol

.. _dev-confdb-syntax-meta-tags:

meta tags
^^^^^^^^^

========  ===================================
Parent    :ref:`meta<dev-confdb-syntax-meta>`
Required  No
Multiple  No
Default:  -
========  ===================================


Contains:

+---------------------------------------------+------------+---------+
| Node                                        | Required   | Multi   |
+=============================================+============+=========+
| :ref:`tag<dev-confdb-syntax-meta-tags-tag>` | Yes        | No      |
+---------------------------------------------+------------+---------+

.. _dev-confdb-syntax-meta-tags-tag:

meta tags \*<tag>
^^^^^^^^^^^^^^^^^

========  ========================================
Parent    :ref:`meta<dev-confdb-syntax-meta-tags>`
Required  Yes
Multiple  Yes
Default:  -
Name      tag
========  ========================================


.. py:function:: make_meta_tag(tag)

    Generate `meta tags \*<tag>` node

    :param tag: meta tags

