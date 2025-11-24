.. _dev-confdb-syntax-system:

system
^^^^^^
Grouping node for system-wide settings

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
| :ref:`hostname<dev-confdb-syntax-system-hostname>`       | No         | No      |
+----------------------------------------------------------+------------+---------+
| :ref:`domain-name<dev-confdb-syntax-system-domain-name>` | No         | No      |
+----------------------------------------------------------+------------+---------+
| :ref:`prompt<dev-confdb-syntax-system-prompt>`           | No         | No      |
+----------------------------------------------------------+------------+---------+
| :ref:`clock<dev-confdb-syntax-system-clock>`             | No         | No      |
+----------------------------------------------------------+------------+---------+
| :ref:`user<dev-confdb-syntax-system-user>`               | No         | No      |
+----------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-hostname:

system hostname
^^^^^^^^^^^^^^^
Grouping node for system hostname settings

========  =======================================
Parent    :ref:`system<dev-confdb-syntax-system>`
Required  No
Multiple  No
Default:  -
========  =======================================


Contains:

+-------------------------------------------------------------+------------+---------+
| Node                                                        | Required   | Multi   |
+=============================================================+============+=========+
| :ref:`hostname<dev-confdb-syntax-system-hostname-hostname>` | Yes        | No      |
+-------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-hostname-hostname:

system hostname <hostname>
^^^^^^^^^^^^^^^^^^^^^^^^^^
System hostname

========  ================================================
Parent    :ref:`system<dev-confdb-syntax-system-hostname>`
Required  Yes
Multiple  No
Default:  -
Name      hostname
========  ================================================


.. py:function:: make_hostname(hostname)

    Generate `system hostname <hostname>` node

    :param hostname: system hostname

.. _dev-confdb-syntax-system-domain-name:

system domain-name
^^^^^^^^^^^^^^^^^^
Grouping node for system domain-name settings

========  =======================================
Parent    :ref:`system<dev-confdb-syntax-system>`
Required  No
Multiple  No
Default:  -
========  =======================================


Contains:

+----------------------------------------------------------------------+------------+---------+
| Node                                                                 | Required   | Multi   |
+======================================================================+============+=========+
| :ref:`domain_name<dev-confdb-syntax-system-domain-name-domain_name>` | Yes        | No      |
+----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-domain-name-domain_name:

system domain-name <domain_name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
System domain name

========  ===================================================
Parent    :ref:`system<dev-confdb-syntax-system-domain-name>`
Required  Yes
Multiple  No
Default:  -
Name      domain_name
========  ===================================================


.. py:function:: make_domain_name(domain_name)

    Generate `system domain-name <domain_name>` node

    :param domain_name: system domain-name

.. _dev-confdb-syntax-system-prompt:

system prompt
^^^^^^^^^^^^^

========  =======================================
Parent    :ref:`system<dev-confdb-syntax-system>`
Required  No
Multiple  No
Default:  -
========  =======================================


Contains:

+-------------------------------------------------------+------------+---------+
| Node                                                  | Required   | Multi   |
+=======================================================+============+=========+
| :ref:`prompt<dev-confdb-syntax-system-prompt-prompt>` | Yes        | No      |
+-------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-prompt-prompt:

system prompt <prompt>
^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================
Parent    :ref:`system<dev-confdb-syntax-system-prompt>`
Required  Yes
Multiple  No
Default:  -
Name      prompt
========  ==============================================


.. py:function:: make_prompt(prompt)

    Generate `system prompt <prompt>` node

    :param prompt: system prompt

.. _dev-confdb-syntax-system-clock:

system clock
^^^^^^^^^^^^

========  =======================================
Parent    :ref:`system<dev-confdb-syntax-system>`
Required  No
Multiple  No
Default:  -
========  =======================================


Contains:

+----------------------------------------------------------+------------+---------+
| Node                                                     | Required   | Multi   |
+==========================================================+============+=========+
| :ref:`timezone<dev-confdb-syntax-system-clock-timezone>` | Yes        | No      |
+----------------------------------------------------------+------------+---------+
| :ref:`source<dev-confdb-syntax-system-clock-source>`     | No         | No      |
+----------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-clock-timezone:

system clock timezone
^^^^^^^^^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`system<dev-confdb-syntax-system-clock>`
Required  Yes
Multiple  No
Default:  -
========  =============================================


Contains:

+-----------------------------------------------------------------+------------+---------+
| Node                                                            | Required   | Multi   |
+=================================================================+============+=========+
| :ref:`tz_name<dev-confdb-syntax-system-clock-timezone-tz_name>` | Yes        | No      |
+-----------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-clock-timezone-tz_name:

system clock timezone <tz_name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================
Parent    :ref:`system<dev-confdb-syntax-system-clock-timezone>`
Required  Yes
Multiple  No
Default:  -
Name      tz_name
========  ======================================================


.. py:function:: make_tz(tz_name)

    Generate `system clock timezone <tz_name>` node

    :param tz_name: system clock timezone


Contains:

+-----------------------------------------------------------------------+------------+---------+
| Node                                                                  | Required   | Multi   |
+=======================================================================+============+=========+
| :ref:`offset<dev-confdb-syntax-system-clock-timezone-tz_name-offset>` | No         | No      |
+-----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-clock-timezone-tz_name-offset:

system clock timezone <tz_name> offset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================
Parent    :ref:`system<dev-confdb-syntax-system-clock-timezone-tz_name>`
Required  No
Multiple  No
Default:  -
========  ==============================================================


Contains:

+------------------------------------------------------------------------------------+------------+---------+
| Node                                                                               | Required   | Multi   |
+====================================================================================+============+=========+
| :ref:`tz_offset<dev-confdb-syntax-system-clock-timezone-tz_name-offset-tz_offset>` | Yes        | No      |
+------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-clock-timezone-tz_name-offset-tz_offset:

system clock timezone <tz_name> offset <tz_offset>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================================
Parent    :ref:`system<dev-confdb-syntax-system-clock-timezone-tz_name-offset>`
Required  Yes
Multiple  No
Default:  -
Name      tz_offset
========  =====================================================================


.. py:function:: make_tz_offset(tz_offset)

    Generate `system clock timezone <tz_name> offset <tz_offset>` node

    :param tz_offset: system clock timezone <tz_name> offset

.. _dev-confdb-syntax-system-clock-source:

system clock source
^^^^^^^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`system<dev-confdb-syntax-system-clock>`
Required  No
Multiple  No
Default:  -
========  =============================================


Contains:

+-------------------------------------------------------------+------------+---------+
| Node                                                        | Required   | Multi   |
+=============================================================+============+=========+
| :ref:`source<dev-confdb-syntax-system-clock-source-source>` | Yes        | No      |
+-------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-clock-source-source:

system clock source <source>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================
Parent    :ref:`system<dev-confdb-syntax-system-clock-source>`
Required  Yes
Multiple  No
Default:  -
Name      source
========  ====================================================


.. py:function:: make_clock_source(source)

    Generate `system clock source <source>` node

    :param source: system clock source

.. _dev-confdb-syntax-system-user:

system user
^^^^^^^^^^^

========  =======================================
Parent    :ref:`system<dev-confdb-syntax-system>`
Required  No
Multiple  No
Default:  -
========  =======================================


Contains:

+---------------------------------------------------------+------------+---------+
| Node                                                    | Required   | Multi   |
+=========================================================+============+=========+
| :ref:`username<dev-confdb-syntax-system-user-username>` | No         | No      |
+---------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-user-username:

system user \*<username>
^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================
Parent    :ref:`system<dev-confdb-syntax-system-user>`
Required  No
Multiple  Yes
Default:  -
Name      username
========  ============================================


Contains:

+------------------------------------------------------------------------------+------------+---------+
| Node                                                                         | Required   | Multi   |
+==============================================================================+============+=========+
| :ref:`uid<dev-confdb-syntax-system-user-username-uid>`                       | No         | Yes     |
+------------------------------------------------------------------------------+------------+---------+
| :ref:`full-name<dev-confdb-syntax-system-user-username-full-name>`           | No         | Yes     |
+------------------------------------------------------------------------------+------------+---------+
| :ref:`class<dev-confdb-syntax-system-user-username-class>`                   | No         | Yes     |
+------------------------------------------------------------------------------+------------+---------+
| :ref:`authentication<dev-confdb-syntax-system-user-username-authentication>` | No         | Yes     |
+------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-user-username-uid:

system user \*<username> uid
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username>`
Required  No
Multiple  No
Default:  -
========  =====================================================


Contains:

+------------------------------------------------------------+------------+---------+
| Node                                                       | Required   | Multi   |
+============================================================+============+=========+
| :ref:`uid<dev-confdb-syntax-system-user-username-uid-uid>` | Yes        | No      |
+------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-user-username-uid-uid:

system user \*<username> uid <uid>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username-uid>`
Required  Yes
Multiple  No
Default:  -
Name      uid
========  =========================================================


.. py:function:: make_user_uid(uid)

    Generate `system user \*<username> uid <uid>` node

    :param uid: system user \*<username> uid

.. _dev-confdb-syntax-system-user-username-full-name:

system user \*<username> full-name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username>`
Required  No
Multiple  No
Default:  -
========  =====================================================


Contains:

+------------------------------------------------------------------------------+------------+---------+
| Node                                                                         | Required   | Multi   |
+==============================================================================+============+=========+
| :ref:`full_name<dev-confdb-syntax-system-user-username-full-name-full_name>` | Yes        | No      |
+------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-user-username-full-name-full_name:

system user \*<username> full-name <full_name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username-full-name>`
Required  Yes
Multiple  No
Default:  -
Name      full_name
========  ===============================================================


.. py:function:: make_user_full_name(full_name)

    Generate `system user \*<username> full-name <full_name>` node

    :param full_name: system user \*<username> full-name

.. _dev-confdb-syntax-system-user-username-class:

system user \*<username> class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username>`
Required  No
Multiple  No
Default:  -
========  =====================================================


Contains:

+----------------------------------------------------------------------------+------------+---------+
| Node                                                                       | Required   | Multi   |
+============================================================================+============+=========+
| :ref:`class_name<dev-confdb-syntax-system-user-username-class-class_name>` | Yes        | No      |
+----------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-user-username-class-class_name:

system user \*<username> class \*<class_name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username-class>`
Required  Yes
Multiple  Yes
Default:  -
Name      class_name
========  ===========================================================


.. py:function:: make_user_class(class_name)

    Generate `system user \*<username> class \*<class_name>` node

    :param class_name: system user \*<username> class

.. _dev-confdb-syntax-system-user-username-authentication:

system user \*<username> authentication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =====================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username>`
Required  No
Multiple  No
Default:  -
========  =====================================================


Contains:

+-----------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                | Required   | Multi   |
+=====================================================================================================+============+=========+
| :ref:`encrypted-password<dev-confdb-syntax-system-user-username-authentication-encrypted-password>` | No         | No      |
+-----------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`ssh-rsa<dev-confdb-syntax-system-user-username-authentication-ssh-rsa>`                       | No         | No      |
+-----------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`ssh-dsa<dev-confdb-syntax-system-user-username-authentication-ssh-dsa>`                       | No         | No      |
+-----------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-user-username-authentication-encrypted-password:

system user \*<username> authentication encrypted-password
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username-authentication>`
Required  No
Multiple  No
Default:  -
========  ====================================================================


Contains:

+----------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                               | Required   | Multi   |
+====================================================================================================+============+=========+
| :ref:`password<dev-confdb-syntax-system-user-username-authentication-encrypted-password-password>` | Yes        | No      |
+----------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-user-username-authentication-encrypted-password-password:

system user \*<username> authentication encrypted-password <password>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username-authentication-encrypted-password>`
Required  Yes
Multiple  No
Default:  -
Name      password
========  =======================================================================================


.. py:function:: make_user_encrypted_password(password)

    Generate `system user \*<username> authentication encrypted-password <password>` node

    :param password: system user \*<username> authentication encrypted-password

.. _dev-confdb-syntax-system-user-username-authentication-ssh-rsa:

system user \*<username> authentication ssh-rsa
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username-authentication>`
Required  No
Multiple  No
Default:  -
========  ====================================================================


Contains:

+-------------------------------------------------------------------------------+------------+---------+
| Node                                                                          | Required   | Multi   |
+===============================================================================+============+=========+
| :ref:`rsa<dev-confdb-syntax-system-user-username-authentication-ssh-rsa-rsa>` | Yes        | No      |
+-------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-user-username-authentication-ssh-rsa-rsa:

system user \*<username> authentication ssh-rsa \*<rsa>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username-authentication-ssh-rsa>`
Required  Yes
Multiple  Yes
Default:  -
Name      rsa
========  ============================================================================


.. py:function:: make_user_ssh_rsa(rsa)

    Generate `system user \*<username> authentication ssh-rsa \*<rsa>` node

    :param rsa: system user \*<username> authentication ssh-rsa

.. _dev-confdb-syntax-system-user-username-authentication-ssh-dsa:

system user \*<username> authentication ssh-dsa
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username-authentication>`
Required  No
Multiple  No
Default:  -
========  ====================================================================


Contains:

+-------------------------------------------------------------------------------+------------+---------+
| Node                                                                          | Required   | Multi   |
+===============================================================================+============+=========+
| :ref:`dsa<dev-confdb-syntax-system-user-username-authentication-ssh-dsa-dsa>` | Yes        | No      |
+-------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-system-user-username-authentication-ssh-dsa-dsa:

system user \*<username> authentication ssh-dsa \*<dsa>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================
Parent    :ref:`system<dev-confdb-syntax-system-user-username-authentication-ssh-dsa>`
Required  Yes
Multiple  Yes
Default:  -
Name      dsa
========  ============================================================================


.. py:function:: make_user_ssh_dsa(dsa)

    Generate `system user \*<username> authentication ssh-dsa \*<dsa>` node

    :param dsa: system user \*<username> authentication ssh-dsa

