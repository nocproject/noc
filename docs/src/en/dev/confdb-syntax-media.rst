.. _dev-confdb-syntax-media:

media
^^^^^

========  ==
Parent    -
Required  No
Multiple  No
Default:  -
========  ==


Contains:

+-------------------------------------------------+------------+---------+
| Node                                            | Required   | Multi   |
+=================================================+============+=========+
| :ref:`sources<dev-confdb-syntax-media-sources>` | No         | No      |
+-------------------------------------------------+------------+---------+
| :ref:`streams<dev-confdb-syntax-media-streams>` | No         | No      |
+-------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources:

media sources
^^^^^^^^^^^^^

========  =====================================
Parent    :ref:`media<dev-confdb-syntax-media>`
Required  No
Multiple  No
Default:  -
========  =====================================


Contains:

+-----------------------------------------------------+------------+---------+
| Node                                                | Required   | Multi   |
+=====================================================+============+=========+
| :ref:`video<dev-confdb-syntax-media-sources-video>` | No         | No      |
+-----------------------------------------------------+------------+---------+
| :ref:`audio<dev-confdb-syntax-media-sources-audio>` | No         | No      |
+-----------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video:

media sources video
^^^^^^^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`media<dev-confdb-syntax-media-sources>`
Required  No
Multiple  No
Default:  -
========  =============================================


Contains:

+---------------------------------------------------------+------------+---------+
| Node                                                    | Required   | Multi   |
+=========================================================+============+=========+
| :ref:`name<dev-confdb-syntax-media-sources-video-name>` | No         | No      |
+---------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name:

media sources video \*<name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video>`
Required  No
Multiple  Yes
Default:  -
Name      name
========  ===================================================


Contains:

+----------------------------------------------------------------------+------------+---------+
| Node                                                                 | Required   | Multi   |
+======================================================================+============+=========+
| :ref:`settings<dev-confdb-syntax-media-sources-video-name-settings>` | No         | Yes     |
+----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings:

media sources video \*<name> settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name>`
Required  No
Multiple  No
Default:  -
========  ========================================================


Contains:

+---------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                          | Required   | Multi   |
+===============================================================================================================+============+=========+
| :ref:`brightness<dev-confdb-syntax-media-sources-video-name-settings-brightness>`                             | No         | No      |
+---------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`saturation<dev-confdb-syntax-media-sources-video-name-settings-saturation>`                             | No         | No      |
+---------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`contrast<dev-confdb-syntax-media-sources-video-name-settings-contrast>`                                 | No         | No      |
+---------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`sharpness<dev-confdb-syntax-media-sources-video-name-settings-sharpness>`                               | No         | No      |
+---------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`white-balance<dev-confdb-syntax-media-sources-video-name-settings-white-balance>`                       | No         | No      |
+---------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`black-light-compensation<dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation>` | No         | No      |
+---------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`wide-dynamic-range<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range>`             | No         | No      |
+---------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-brightness:

media sources video \*<name> settings brightness
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+----------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                         | Required   | Multi   |
+==============================================================================================+============+=========+
| :ref:`brightness<dev-confdb-syntax-media-sources-video-name-settings-brightness-brightness>` | Yes        | No      |
+----------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-brightness-brightness:

media sources video \*<name> settings brightness <brightness>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-brightness>`
Required  Yes
Multiple  No
Default:  -
Name      brightness
========  ============================================================================


.. py:function:: make_video_brightness(brightness)

    Generate `media sources video \*<name> settings brightness <brightness>` node

    :param brightness: media sources video \*<name> settings brightness

.. _dev-confdb-syntax-media-sources-video-name-settings-saturation:

media sources video \*<name> settings saturation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+----------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                         | Required   | Multi   |
+==============================================================================================+============+=========+
| :ref:`saturation<dev-confdb-syntax-media-sources-video-name-settings-saturation-saturation>` | Yes        | No      |
+----------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-saturation-saturation:

media sources video \*<name> settings saturation <saturation>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-saturation>`
Required  Yes
Multiple  No
Default:  -
Name      saturation
========  ============================================================================


.. py:function:: make_video_saturation(saturation)

    Generate `media sources video \*<name> settings saturation <saturation>` node

    :param saturation: media sources video \*<name> settings saturation

.. _dev-confdb-syntax-media-sources-video-name-settings-contrast:

media sources video \*<name> settings contrast
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+----------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                   | Required   | Multi   |
+========================================================================================+============+=========+
| :ref:`contrast<dev-confdb-syntax-media-sources-video-name-settings-contrast-contrast>` | Yes        | No      |
+----------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-contrast-contrast:

media sources video \*<name> settings contrast <contrast>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-contrast>`
Required  Yes
Multiple  No
Default:  -
Name      contrast
========  ==========================================================================


.. py:function:: make_video_contrast(contrast)

    Generate `media sources video \*<name> settings contrast <contrast>` node

    :param contrast: media sources video \*<name> settings contrast

.. _dev-confdb-syntax-media-sources-video-name-settings-sharpness:

media sources video \*<name> settings sharpness
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+-------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                      | Required   | Multi   |
+===========================================================================================+============+=========+
| :ref:`sharpness<dev-confdb-syntax-media-sources-video-name-settings-sharpness-sharpness>` | Yes        | No      |
+-------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-sharpness-sharpness:

media sources video \*<name> settings sharpness <sharpness>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-sharpness>`
Required  Yes
Multiple  No
Default:  -
Name      sharpness
========  ===========================================================================


.. py:function:: make_video_sharpness(sharpness)

    Generate `media sources video \*<name> settings sharpness <sharpness>` node

    :param sharpness: media sources video \*<name> settings sharpness

.. _dev-confdb-syntax-media-sources-video-name-settings-white-balance:

media sources video \*<name> settings white-balance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+-----------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                | Required   | Multi   |
+=====================================================================================================+============+=========+
| :ref:`admin-status<dev-confdb-syntax-media-sources-video-name-settings-white-balance-admin-status>` | No         | No      |
+-----------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`auto<dev-confdb-syntax-media-sources-video-name-settings-white-balance-auto>`                 | No         | No      |
+-----------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`cr-gain<dev-confdb-syntax-media-sources-video-name-settings-white-balance-cr-gain>`           | No         | No      |
+-----------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`gb-gain<dev-confdb-syntax-media-sources-video-name-settings-white-balance-gb-gain>`           | No         | No      |
+-----------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-white-balance-admin-status:

media sources video \*<name> settings white-balance admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-white-balance>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                             | Required   | Multi   |
+==================================================================================================================+============+=========+
| :ref:`admin_status<dev-confdb-syntax-media-sources-video-name-settings-white-balance-admin-status-admin_status>` | Yes        | No      |
+------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-white-balance-admin-status-admin_status:

media sources video \*<name> settings white-balance admin-status <admin_status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-white-balance-admin-status>`
Required  Yes
Multiple  No
Default:  -
Name      admin_status
========  ============================================================================================


.. py:function:: make_video_white_balance_admin_status(admin_status)

    Generate `media sources video \*<name> settings white-balance admin-status <admin_status>` node

    :param admin_status: media sources video \*<name> settings white-balance admin-status

.. _dev-confdb-syntax-media-sources-video-name-settings-white-balance-auto:

media sources video \*<name> settings white-balance auto
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-white-balance>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


.. py:function:: make_video_white_balance_auto(None)

    Generate `media sources video \*<name> settings white-balance auto` node

    :param None: media sources video \*<name> settings white-balance

.. _dev-confdb-syntax-media-sources-video-name-settings-white-balance-cr-gain:

media sources video \*<name> settings white-balance cr-gain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-white-balance>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+---------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                              | Required   | Multi   |
+===================================================================================================+============+=========+
| :ref:`cr_gain<dev-confdb-syntax-media-sources-video-name-settings-white-balance-cr-gain-cr_gain>` | Yes        | No      |
+---------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-white-balance-cr-gain-cr_gain:

media sources video \*<name> settings white-balance cr-gain <cr_gain>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-white-balance-cr-gain>`
Required  Yes
Multiple  No
Default:  -
Name      cr_gain
========  =======================================================================================


.. py:function:: make_video_white_balance_cr_gain(cr_gain)

    Generate `media sources video \*<name> settings white-balance cr-gain <cr_gain>` node

    :param cr_gain: media sources video \*<name> settings white-balance cr-gain

.. _dev-confdb-syntax-media-sources-video-name-settings-white-balance-gb-gain:

media sources video \*<name> settings white-balance gb-gain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-white-balance>`
Required  No
Multiple  No
Default:  -
========  ===============================================================================


Contains:

+---------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                              | Required   | Multi   |
+===================================================================================================+============+=========+
| :ref:`gb_gain<dev-confdb-syntax-media-sources-video-name-settings-white-balance-gb-gain-gb_gain>` | Yes        | No      |
+---------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-white-balance-gb-gain-gb_gain:

media sources video \*<name> settings white-balance gb-gain <gb_gain>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-white-balance-gb-gain>`
Required  Yes
Multiple  No
Default:  -
Name      gb_gain
========  =======================================================================================


.. py:function:: make_video_white_balance_gb_gain(gb_gain)

    Generate `media sources video \*<name> settings white-balance gb-gain <gb_gain>` node

    :param gb_gain: media sources video \*<name> settings white-balance gb-gain

.. _dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation:

media sources video \*<name> settings black-light-compensation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+----------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                           | Required   | Multi   |
+================================================================================================================+============+=========+
| :ref:`admin-status<dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation-admin-status>` | No         | No      |
+----------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation-admin-status:

media sources video \*<name> settings black-light-compensation admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation>`
Required  No
Multiple  No
Default:  -
========  ==========================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                        | Required   | Multi   |
+=============================================================================================================================+============+=========+
| :ref:`admin_status<dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation-admin-status-admin_status>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation-admin-status-admin_status:

media sources video \*<name> settings black-light-compensation admin-status <admin_status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-black-light-compensation-admin-status>`
Required  Yes
Multiple  No
Default:  -
Name      admin_status
========  =======================================================================================================


.. py:function:: make_video_black_light_compensation_admin_status(admin_status)

    Generate `media sources video \*<name> settings black-light-compensation admin-status <admin_status>` node

    :param admin_status: media sources video \*<name> settings black-light-compensation admin-status

.. _dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range:

media sources video \*<name> settings wide-dynamic-range
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+----------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                     | Required   | Multi   |
+==========================================================================================================+============+=========+
| :ref:`admin-status<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-admin-status>` | No         | No      |
+----------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`level<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-level>`               | No         | No      |
+----------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-admin-status:

media sources video \*<name> settings wide-dynamic-range admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range>`
Required  No
Multiple  No
Default:  -
========  ====================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                  | Required   | Multi   |
+=======================================================================================================================+============+=========+
| :ref:`admin_status<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-admin-status-admin_status>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-admin-status-admin_status:

media sources video \*<name> settings wide-dynamic-range admin-status <admin_status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-admin-status>`
Required  Yes
Multiple  No
Default:  -
Name      admin_status
========  =================================================================================================


.. py:function:: make_video_wide_dynamic_range_admin_status(admin_status)

    Generate `media sources video \*<name> settings wide-dynamic-range admin-status <admin_status>` node

    :param admin_status: media sources video \*<name> settings wide-dynamic-range admin-status

.. _dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-level:

media sources video \*<name> settings wide-dynamic-range level
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range>`
Required  No
Multiple  No
Default:  -
========  ====================================================================================


Contains:

+--------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                             | Required   | Multi   |
+==================================================================================================+============+=========+
| :ref:`level<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-level-level>` | Yes        | No      |
+--------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-level-level:

media sources video \*<name> settings wide-dynamic-range level <level>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-video-name-settings-wide-dynamic-range-level>`
Required  Yes
Multiple  No
Default:  -
Name      level
========  ==========================================================================================


.. py:function:: make_video_wide_dynamic_range_level(level)

    Generate `media sources video \*<name> settings wide-dynamic-range level <level>` node

    :param level: media sources video \*<name> settings wide-dynamic-range level

.. _dev-confdb-syntax-media-sources-audio:

media sources audio
^^^^^^^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`media<dev-confdb-syntax-media-sources>`
Required  No
Multiple  No
Default:  -
========  =============================================


Contains:

+---------------------------------------------------------+------------+---------+
| Node                                                    | Required   | Multi   |
+=========================================================+============+=========+
| :ref:`name<dev-confdb-syntax-media-sources-audio-name>` | No         | No      |
+---------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-audio-name:

media sources audio \*<name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-audio>`
Required  No
Multiple  Yes
Default:  -
Name      name
========  ===================================================


Contains:

+----------------------------------------------------------------------+------------+---------+
| Node                                                                 | Required   | Multi   |
+======================================================================+============+=========+
| :ref:`source<dev-confdb-syntax-media-sources-audio-name-source>`     | No         | Yes     |
+----------------------------------------------------------------------+------------+---------+
| :ref:`settings<dev-confdb-syntax-media-sources-audio-name-settings>` | No         | Yes     |
+----------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-audio-name-source:

media sources audio \*<name> source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-audio-name>`
Required  No
Multiple  No
Default:  -
========  ========================================================


Contains:

+-------------------------------------------------------------------------+------------+---------+
| Node                                                                    | Required   | Multi   |
+=========================================================================+============+=========+
| :ref:`source<dev-confdb-syntax-media-sources-audio-name-source-source>` | Yes        | No      |
+-------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-audio-name-source-source:

media sources audio \*<name> source <source>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-audio-name-source>`
Required  Yes
Multiple  No
Default:  -
Name      source
========  ===============================================================


.. py:function:: make_audio_source(source)

    Generate `media sources audio \*<name> source <source>` node

    :param source: media sources audio \*<name> source

.. _dev-confdb-syntax-media-sources-audio-name-settings:

media sources audio \*<name> settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-audio-name>`
Required  No
Multiple  No
Default:  -
========  ========================================================


Contains:

+---------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                        | Required   | Multi   |
+=============================================================================================+============+=========+
| :ref:`volume<dev-confdb-syntax-media-sources-audio-name-settings-volume>`                   | No         | No      |
+---------------------------------------------------------------------------------------------+------------+---------+
| :ref:`noise-reduction<dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction>` | No         | No      |
+---------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-audio-name-settings-volume:

media sources audio \*<name> settings volume
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-audio-name-settings>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+----------------------------------------------------------------------------------+------------+---------+
| Node                                                                             | Required   | Multi   |
+==================================================================================+============+=========+
| :ref:`volume<dev-confdb-syntax-media-sources-audio-name-settings-volume-volume>` | Yes        | No      |
+----------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-audio-name-settings-volume-volume:

media sources audio \*<name> settings volume <volume>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ========================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-audio-name-settings-volume>`
Required  Yes
Multiple  No
Default:  -
Name      volume
========  ========================================================================


.. py:function:: make_audio_volume(volume)

    Generate `media sources audio \*<name> settings volume <volume>` node

    :param volume: media sources audio \*<name> settings volume

.. _dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction:

media sources audio \*<name> settings noise-reduction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-audio-name-settings>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+-------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                  | Required   | Multi   |
+=======================================================================================================+============+=========+
| :ref:`admin-status<dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction-admin-status>` | No         | No      |
+-------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction-admin-status:

media sources audio \*<name> settings noise-reduction admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction>`
Required  No
Multiple  No
Default:  -
========  =================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                               | Required   | Multi   |
+====================================================================================================================+============+=========+
| :ref:`admin_status<dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction-admin-status-admin_status>` | Yes        | No      |
+--------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction-admin-status-admin_status:

media sources audio \*<name> settings noise-reduction admin-status <admin_status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-sources-audio-name-settings-noise-reduction-admin-status>`
Required  Yes
Multiple  No
Default:  -
Name      admin_status
========  ==============================================================================================


.. py:function:: make_audio_noise_reduction_admin_status(admin_status)

    Generate `media sources audio \*<name> settings noise-reduction admin-status <admin_status>` node

    :param admin_status: media sources audio \*<name> settings noise-reduction admin-status

.. _dev-confdb-syntax-media-streams:

media streams
^^^^^^^^^^^^^

========  =====================================
Parent    :ref:`media<dev-confdb-syntax-media>`
Required  No
Multiple  No
Default:  -
========  =====================================


Contains:

+---------------------------------------------------+------------+---------+
| Node                                              | Required   | Multi   |
+===================================================+============+=========+
| :ref:`name<dev-confdb-syntax-media-streams-name>` | No         | No      |
+---------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name:

media streams \*<name>
^^^^^^^^^^^^^^^^^^^^^^

========  =============================================
Parent    :ref:`media<dev-confdb-syntax-media-streams>`
Required  No
Multiple  Yes
Default:  -
Name      name
========  =============================================


Contains:

+------------------------------------------------------------------+------------+---------+
| Node                                                             | Required   | Multi   |
+==================================================================+============+=========+
| :ref:`rtsp-path<dev-confdb-syntax-media-streams-name-rtsp-path>` | No         | Yes     |
+------------------------------------------------------------------+------------+---------+
| :ref:`settings<dev-confdb-syntax-media-streams-name-settings>`   | No         | Yes     |
+------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-rtsp-path:

media streams \*<name> rtsp-path
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name>`
Required  No
Multiple  No
Default:  -
========  ==================================================


Contains:

+------------------------------------------------------------------+------------+---------+
| Node                                                             | Required   | Multi   |
+==================================================================+============+=========+
| :ref:`path<dev-confdb-syntax-media-streams-name-rtsp-path-path>` | Yes        | No      |
+------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-rtsp-path-path:

media streams \*<name> rtsp-path <path>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-rtsp-path>`
Required  Yes
Multiple  No
Default:  -
Name      path
========  ============================================================


.. py:function:: make_stream_rtsp_path(path)

    Generate `media streams \*<name> rtsp-path <path>` node

    :param path: media streams \*<name> rtsp-path

.. _dev-confdb-syntax-media-streams-name-settings:

media streams \*<name> settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name>`
Required  No
Multiple  No
Default:  -
========  ==================================================


Contains:

+-------------------------------------------------------------------------+------------+---------+
| Node                                                                    | Required   | Multi   |
+=========================================================================+============+=========+
| :ref:`video<dev-confdb-syntax-media-streams-name-settings-video>`       | No         | No      |
+-------------------------------------------------------------------------+------------+---------+
| :ref:`audio<dev-confdb-syntax-media-streams-name-settings-audio>`       | No         | No      |
+-------------------------------------------------------------------------+------------+---------+
| :ref:`overlays<dev-confdb-syntax-media-streams-name-settings-overlays>` | No         | No      |
+-------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video:

media streams \*<name> settings video
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings>`
Required  No
Multiple  No
Default:  -
========  ===========================================================


Contains:

+---------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                  | Required   | Multi   |
+=======================================================================================+============+=========+
| :ref:`admin-status<dev-confdb-syntax-media-streams-name-settings-video-admin-status>` | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+
| :ref:`resolution<dev-confdb-syntax-media-streams-name-settings-video-resolution>`     | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+
| :ref:`codec<dev-confdb-syntax-media-streams-name-settings-video-codec>`               | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+
| :ref:`rate-control<dev-confdb-syntax-media-streams-name-settings-video-rate-control>` | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-admin-status:

media streams \*<name> settings video admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+----------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                               | Required   | Multi   |
+====================================================================================================+============+=========+
| :ref:`admin_status<dev-confdb-syntax-media-streams-name-settings-video-admin-status-admin_status>` | Yes        | No      |
+----------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-admin-status-admin_status:

media streams \*<name> settings video admin-status <admin_status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-admin-status>`
Required  Yes
Multiple  No
Default:  -
Name      admin_status
========  ==============================================================================


.. py:function:: make_media_streams_video_admin_status(admin_status)

    Generate `media streams \*<name> settings video admin-status <admin_status>` node

    :param admin_status: media streams \*<name> settings video admin-status

.. _dev-confdb-syntax-media-streams-name-settings-video-resolution:

media streams \*<name> settings video resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+--------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                 | Required   | Multi   |
+======================================================================================+============+=========+
| :ref:`width<dev-confdb-syntax-media-streams-name-settings-video-resolution-width>`   | No         | No      |
+--------------------------------------------------------------------------------------+------------+---------+
| :ref:`height<dev-confdb-syntax-media-streams-name-settings-video-resolution-height>` | No         | No      |
+--------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-resolution-width:

media streams \*<name> settings video resolution width
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-resolution>`
Required  No
Multiple  No
Default:  -
========  ============================================================================


Contains:

+------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                     | Required   | Multi   |
+==========================================================================================+============+=========+
| :ref:`width<dev-confdb-syntax-media-streams-name-settings-video-resolution-width-width>` | Yes        | No      |
+------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-resolution-width-width:

media streams \*<name> settings video resolution width <width>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-resolution-width>`
Required  Yes
Multiple  No
Default:  -
Name      width
========  ==================================================================================


.. py:function:: make_media_streams_video_resolution_width(width)

    Generate `media streams \*<name> settings video resolution width <width>` node

    :param width: media streams \*<name> settings video resolution width

.. _dev-confdb-syntax-media-streams-name-settings-video-resolution-height:

media streams \*<name> settings video resolution height
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-resolution>`
Required  No
Multiple  No
Default:  -
========  ============================================================================


Contains:

+---------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                        | Required   | Multi   |
+=============================================================================================+============+=========+
| :ref:`height<dev-confdb-syntax-media-streams-name-settings-video-resolution-height-height>` | Yes        | No      |
+---------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-resolution-height-height:

media streams \*<name> settings video resolution height <height>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-resolution-height>`
Required  Yes
Multiple  No
Default:  -
Name      height
========  ===================================================================================


.. py:function:: make_media_streams_video_resolution_height(height)

    Generate `media streams \*<name> settings video resolution height <height>` node

    :param height: media streams \*<name> settings video resolution height

.. _dev-confdb-syntax-media-streams-name-settings-video-codec:

media streams \*<name> settings video codec
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+-------------------------------------------------------------------------------+------------+---------+
| Node                                                                          | Required   | Multi   |
+===============================================================================+============+=========+
| :ref:`mpeg4<dev-confdb-syntax-media-streams-name-settings-video-codec-mpeg4>` | No         | No      |
+-------------------------------------------------------------------------------+------------+---------+
| :ref:`h264<dev-confdb-syntax-media-streams-name-settings-video-codec-h264>`   | No         | No      |
+-------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-mpeg4:

media streams \*<name> settings video codec mpeg4
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec>`
Required  No
Multiple  No
Default:  -
========  =======================================================================


.. py:function:: make_media_streams_video_codec_mpeg4(None)

    Generate `media streams \*<name> settings video codec mpeg4` node

    :param None: media streams \*<name> settings video codec

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-h264:

media streams \*<name> settings video codec h264
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec>`
Required  No
Multiple  No
Default:  -
========  =======================================================================


.. py:function:: make_media_streams_video_codec_h264(None)

    Generate `media streams \*<name> settings video codec h264` node

    :param None: media streams \*<name> settings video codec


Contains:

+----------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                   | Required   | Multi   |
+========================================================================================+============+=========+
| :ref:`profile<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile>` | No         | No      |
+----------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile:

media streams \*<name> settings video codec h264 profile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec-h264>`
Required  No
Multiple  No
Default:  -
========  ============================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                         | Required   | Multi   |
+==============================================================================================================+============+=========+
| :ref:`name<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-name>`                     | No         | No      |
+--------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`id<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-id>`                         | No         | No      |
+--------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`constraint-set<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-constraint-set>` | No         | No      |
+--------------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`gov-length<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-gov-length>`         | No         | No      |
+--------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-name:

media streams \*<name> settings video codec h264 profile name
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile>`
Required  No
Multiple  No
Default:  -
========  ====================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                | Required   | Multi   |
+=====================================================================================================+============+=========+
| :ref:`profile<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-name-profile>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-name-profile:

media streams \*<name> settings video codec h264 profile name <profile>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-name>`
Required  Yes
Multiple  No
Default:  -
Name      profile
========  =========================================================================================


.. py:function:: make_media_streams_video_codec_h264_profile_name(profile)

    Generate `media streams \*<name> settings video codec h264 profile name <profile>` node

    :param profile: media streams \*<name> settings video codec h264 profile name

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-id:

media streams \*<name> settings video codec h264 profile id
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile>`
Required  No
Multiple  No
Default:  -
========  ====================================================================================


Contains:

+-----------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                    | Required   | Multi   |
+=========================================================================================+============+=========+
| :ref:`id<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-id-id>` | Yes        | No      |
+-----------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-id-id:

media streams \*<name> settings video codec h264 profile id <id>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-id>`
Required  Yes
Multiple  No
Default:  -
Name      id
========  =======================================================================================


.. py:function:: make_media_streams_video_codec_h264_profile_id(id)

    Generate `media streams \*<name> settings video codec h264 profile id <id>` node

    :param id: media streams \*<name> settings video codec h264 profile id

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-constraint-set:

media streams \*<name> settings video codec h264 profile constraint-set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile>`
Required  No
Multiple  No
Default:  -
========  ====================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                  | Required   | Multi   |
+=======================================================================================================================+============+=========+
| :ref:`constraints<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-constraint-set-constraints>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-constraint-set-constraints:

media streams \*<name> settings video codec h264 profile constraint-set <constraints>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-constraint-set>`
Required  Yes
Multiple  No
Default:  -
Name      constraints
========  ===================================================================================================


.. py:function:: make_media_streams_video_codec_h264_profile_constrains(constraints)

    Generate `media streams \*<name> settings video codec h264 profile constraint-set <constraints>` node

    :param constraints: media streams \*<name> settings video codec h264 profile constraint-set

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-gov-length:

media streams \*<name> settings video codec h264 profile gov-length
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile>`
Required  No
Multiple  No
Default:  -
========  ====================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                            | Required   | Multi   |
+=================================================================================================================+============+=========+
| :ref:`gov_length<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-gov-length-gov_length>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-gov-length-gov_length:

media streams \*<name> settings video codec h264 profile gov-length <gov_length>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-codec-h264-profile-gov-length>`
Required  Yes
Multiple  No
Default:  -
Name      gov_length
========  ===============================================================================================


.. py:function:: make_media_streams_video_codec_h264_profile_gov_length(gov_length)

    Generate `media streams \*<name> settings video codec h264 profile gov-length <gov_length>` node

    :param gov_length: media streams \*<name> settings video codec h264 profile gov-length

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control:

media streams \*<name> settings video rate-control
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                 | Required   | Multi   |
+======================================================================================================+============+=========+
| :ref:`min-framerate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-min-framerate>` | No         | No      |
+------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`max-framerate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-max-framerate>` | No         | No      |
+------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`mode<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode>`                   | No         | No      |
+------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-min-framerate:

media streams \*<name> settings video rate-control min-framerate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control>`
Required  No
Multiple  No
Default:  -
========  ==============================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                               | Required   | Multi   |
+====================================================================================================================+============+=========+
| :ref:`min_framerate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-min-framerate-min_framerate>` | No         | No      |
+--------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-min-framerate-min_framerate:

media streams \*<name> settings video rate-control min-framerate <min_framerate>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control-min-framerate>`
Required  No
Multiple  No
Default:  -
Name      min_framerate
========  ============================================================================================


.. py:function:: make_media_streams_video_rate_control_min_framerate(min_framerate)

    Generate `media streams \*<name> settings video rate-control min-framerate <min_framerate>` node

    :param min_framerate: media streams \*<name> settings video rate-control min-framerate

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-max-framerate:

media streams \*<name> settings video rate-control max-framerate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control>`
Required  No
Multiple  No
Default:  -
========  ==============================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                               | Required   | Multi   |
+====================================================================================================================+============+=========+
| :ref:`max_framerate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-max-framerate-max_framerate>` | Yes        | No      |
+--------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-max-framerate-max_framerate:

media streams \*<name> settings video rate-control max-framerate <max_framerate>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control-max-framerate>`
Required  Yes
Multiple  No
Default:  -
Name      max_framerate
========  ============================================================================================


.. py:function:: make_media_streams_video_rate_control_max_framerate(max_framerate)

    Generate `media streams \*<name> settings video rate-control max-framerate <max_framerate>` node

    :param max_framerate: media streams \*<name> settings video rate-control max-framerate

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode:

media streams \*<name> settings video rate-control mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control>`
Required  No
Multiple  No
Default:  -
========  ==============================================================================


Contains:

+---------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                  | Required   | Multi   |
+=======================================================================================+============+=========+
| :ref:`cbr<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr>` | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+
| :ref:`vbr<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr>` | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr:

media streams \*<name> settings video rate-control mode cbr
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode>`
Required  No
Multiple  No
Default:  -
========  ===================================================================================


Contains:

+---------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                              | Required   | Multi   |
+===================================================================================================+============+=========+
| :ref:`bitrate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr-bitrate>` | No         | No      |
+---------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr-bitrate:

media streams \*<name> settings video rate-control mode cbr bitrate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                      | Required   | Multi   |
+===========================================================================================================+============+=========+
| :ref:`bitrate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr-bitrate-bitrate>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr-bitrate-bitrate:

media streams \*<name> settings video rate-control mode cbr bitrate <bitrate>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===============================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-cbr-bitrate>`
Required  Yes
Multiple  No
Default:  -
Name      bitrate
========  ===============================================================================================


.. py:function:: make_media_streams_video_rate_control_cbr_bitrate(bitrate)

    Generate `media streams \*<name> settings video rate-control mode cbr bitrate <bitrate>` node

    :param bitrate: media streams \*<name> settings video rate-control mode cbr bitrate

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr:

media streams \*<name> settings video rate-control mode vbr
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode>`
Required  No
Multiple  No
Default:  -
========  ===================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                      | Required   | Multi   |
+===========================================================================================================+============+=========+
| :ref:`max-bitrate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr-max-bitrate>` | No         | No      |
+-----------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr-max-bitrate:

media streams \*<name> settings video rate-control mode vbr max-bitrate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr>`
Required  No
Multiple  No
Default:  -
========  =======================================================================================


Contains:

+-----------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                                  | Required   | Multi   |
+=======================================================================================================================+============+=========+
| :ref:`max_bitrate<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr-max-bitrate-max_bitrate>` | Yes        | No      |
+-----------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr-max-bitrate-max_bitrate:

media streams \*<name> settings video rate-control mode vbr max-bitrate <max_bitrate>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===================================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-video-rate-control-mode-vbr-max-bitrate>`
Required  Yes
Multiple  No
Default:  -
Name      max_bitrate
========  ===================================================================================================


.. py:function:: make_media_streams_video_rate_control_vbr_max_bitrate(max_bitrate)

    Generate `media streams \*<name> settings video rate-control mode vbr max-bitrate <max_bitrate>` node

    :param max_bitrate: media streams \*<name> settings video rate-control mode vbr max-bitrate

.. _dev-confdb-syntax-media-streams-name-settings-audio:

media streams \*<name> settings audio
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings>`
Required  No
Multiple  No
Default:  -
========  ===========================================================


Contains:

+---------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                  | Required   | Multi   |
+=======================================================================================+============+=========+
| :ref:`admin-status<dev-confdb-syntax-media-streams-name-settings-audio-admin-status>` | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+
| :ref:`codec<dev-confdb-syntax-media-streams-name-settings-audio-codec>`               | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+
| :ref:`bitrate<dev-confdb-syntax-media-streams-name-settings-audio-bitrate>`           | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+
| :ref:`samplerate<dev-confdb-syntax-media-streams-name-settings-audio-samplerate>`     | No         | No      |
+---------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-audio-admin-status:

media streams \*<name> settings audio admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-audio>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+----------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                               | Required   | Multi   |
+====================================================================================================+============+=========+
| :ref:`admin_status<dev-confdb-syntax-media-streams-name-settings-audio-admin-status-admin_status>` | Yes        | No      |
+----------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-audio-admin-status-admin_status:

media streams \*<name> settings audio admin-status <admin_status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-audio-admin-status>`
Required  Yes
Multiple  No
Default:  -
Name      admin_status
========  ==============================================================================


.. py:function:: make_media_streams_audio_admin_status(admin_status)

    Generate `media streams \*<name> settings audio admin-status <admin_status>` node

    :param admin_status: media streams \*<name> settings audio admin-status

.. _dev-confdb-syntax-media-streams-name-settings-audio-codec:

media streams \*<name> settings audio codec
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-audio>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+-------------------------------------------------------------------------------+------------+---------+
| Node                                                                          | Required   | Multi   |
+===============================================================================+============+=========+
| :ref:`codec<dev-confdb-syntax-media-streams-name-settings-audio-codec-codec>` | Yes        | No      |
+-------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-audio-codec-codec:

media streams \*<name> settings audio codec <codec>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =======================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-audio-codec>`
Required  Yes
Multiple  No
Default:  -
Name      codec
========  =======================================================================


.. py:function:: make_media_streams_audio_codec(codec)

    Generate `media streams \*<name> settings audio codec <codec>` node

    :param codec: media streams \*<name> settings audio codec

.. _dev-confdb-syntax-media-streams-name-settings-audio-bitrate:

media streams \*<name> settings audio bitrate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-audio>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+-------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                | Required   | Multi   |
+=====================================================================================+============+=========+
| :ref:`bitrate<dev-confdb-syntax-media-streams-name-settings-audio-bitrate-bitrate>` | No         | No      |
+-------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-audio-bitrate-bitrate:

media streams \*<name> settings audio bitrate <bitrate>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =========================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-audio-bitrate>`
Required  No
Multiple  No
Default:  -
Name      bitrate
========  =========================================================================


.. py:function:: make_media_streams_audio_bitrate(bitrate)

    Generate `media streams \*<name> settings audio bitrate <bitrate>` node

    :param bitrate: media streams \*<name> settings audio bitrate

.. _dev-confdb-syntax-media-streams-name-settings-audio-samplerate:

media streams \*<name> settings audio samplerate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-audio>`
Required  No
Multiple  No
Default:  -
========  =================================================================


Contains:

+----------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                         | Required   | Multi   |
+==============================================================================================+============+=========+
| :ref:`samplerate<dev-confdb-syntax-media-streams-name-settings-audio-samplerate-samplerate>` | No         | No      |
+----------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-audio-samplerate-samplerate:

media streams \*<name> settings audio samplerate <samplerate>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-audio-samplerate>`
Required  No
Multiple  No
Default:  -
Name      samplerate
========  ============================================================================


.. py:function:: make_media_streams_audio_samplerate(samplerate)

    Generate `media streams \*<name> settings audio samplerate <samplerate>` node

    :param samplerate: media streams \*<name> settings audio samplerate

.. _dev-confdb-syntax-media-streams-name-settings-overlays:

media streams \*<name> settings overlays
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ===========================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings>`
Required  No
Multiple  No
Default:  -
========  ===========================================================


Contains:

+------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                     | Required   | Multi   |
+==========================================================================================+============+=========+
| :ref:`overlay_name<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name>` | No         | No      |
+------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name:

media streams \*<name> settings overlays <overlay_name>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ====================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-overlays>`
Required  No
Multiple  No
Default:  -
Name      overlay_name
========  ====================================================================


Contains:

+-------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                  | Required   | Multi   |
+=======================================================================================================+============+=========+
| :ref:`admin-status<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-admin-status>` | No         | No      |
+-------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`position<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position>`         | No         | No      |
+-------------------------------------------------------------------------------------------------------+------------+---------+
| :ref:`text<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-text>`                 | No         | No      |
+-------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-admin-status:

media streams \*<name> settings overlays <overlay_name> admin-status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name>`
Required  No
Multiple  No
Default:  -
========  =================================================================================


Contains:

+--------------------------------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                                               | Required   | Multi   |
+====================================================================================================================+============+=========+
| :ref:`admin_status<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-admin-status-admin_status>` | Yes        | No      |
+--------------------------------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-admin-status-admin_status:

media streams \*<name> settings overlays <overlay_name> admin-status <admin_status>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==============================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-admin-status>`
Required  Yes
Multiple  No
Default:  -
Name      admin_status
========  ==============================================================================================


.. py:function:: make_media_streams_overlay_status(admin_status)

    Generate `media streams \*<name> settings overlays <overlay_name> admin-status <admin_status>` node

    :param admin_status: media streams \*<name> settings overlays <overlay_name> admin-status

.. _dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position:

media streams \*<name> settings overlays <overlay_name> position
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name>`
Required  No
Multiple  No
Default:  -
========  =================================================================================


Contains:

+------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                     | Required   | Multi   |
+==========================================================================================+============+=========+
| :ref:`x<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-x>` | No         | No      |
+------------------------------------------------------------------------------------------+------------+---------+
| :ref:`y<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-y>` | No         | No      |
+------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-x:

media streams \*<name> settings overlays <overlay_name> position x
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position>`
Required  No
Multiple  No
Default:  -
========  ==========================================================================================


Contains:

+--------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                       | Required   | Multi   |
+============================================================================================+============+=========+
| :ref:`x<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-x-x>` | Yes        | No      |
+--------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-x-x:

media streams \*<name> settings overlays <overlay_name> position x <x>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-x>`
Required  Yes
Multiple  No
Default:  -
Name      x
========  ============================================================================================


.. py:function:: make_media_streams_overlay_position_x(x)

    Generate `media streams \*<name> settings overlays <overlay_name> position x <x>` node

    :param x: media streams \*<name> settings overlays <overlay_name> position x

.. _dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-y:

media streams \*<name> settings overlays <overlay_name> position y
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ==========================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position>`
Required  No
Multiple  No
Default:  -
========  ==========================================================================================


Contains:

+--------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                       | Required   | Multi   |
+============================================================================================+============+=========+
| :ref:`y<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-y-y>` | Yes        | No      |
+--------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-y-y:

media streams \*<name> settings overlays <overlay_name> position y <y>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ============================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-position-y>`
Required  Yes
Multiple  No
Default:  -
Name      y
========  ============================================================================================


.. py:function:: make_media_streams_overlay_position_y(y)

    Generate `media streams \*<name> settings overlays <overlay_name> position y <y>` node

    :param y: media streams \*<name> settings overlays <overlay_name> position y

.. _dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-text:

media streams \*<name> settings overlays <overlay_name> text
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  =================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name>`
Required  No
Multiple  No
Default:  -
========  =================================================================================


Contains:

+--------------------------------------------------------------------------------------------+------------+---------+
| Node                                                                                       | Required   | Multi   |
+============================================================================================+============+=========+
| :ref:`text<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-text-text>` | Yes        | No      |
+--------------------------------------------------------------------------------------------+------------+---------+

.. _dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-text-text:

media streams \*<name> settings overlays <overlay_name> text <text>
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========  ======================================================================================
Parent    :ref:`media<dev-confdb-syntax-media-streams-name-settings-overlays-overlay_name-text>`
Required  Yes
Multiple  No
Default:  -
Name      text
========  ======================================================================================


.. py:function:: make_media_streams_overlay_text(text)

    Generate `media streams \*<name> settings overlays <overlay_name> text <text>` node

    :param text: media streams \*<name> settings overlays <overlay_name> text

