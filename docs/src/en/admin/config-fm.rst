.. _config-fm:

fm
--


.. _config-fm-active_window:

active_window
~~~~~~~~~~~~~

==================  ====================
**YAML Path**       fm.active_window
**Key-Value Path**  fm/active_window
**Environment**     NOC_FM_ACTIVE_WINDOW
**Default Value**   1d
==================  ====================


.. _config-fm-keep_events_wo_alarm:

keep_events_wo_alarm
~~~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       fm.keep_events_wo_alarm
**Key-Value Path**  fm/keep_events_wo_alarm
**Environment**     NOC_FM_KEEP_EVENTS_WO_ALARM
**Default Value**   0
==================  ===========================


.. _config-fm-keep_events_with_alarm:

keep_events_with_alarm
~~~~~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       fm.keep_events_with_alarm
**Key-Value Path**  fm/keep_events_with_alarm
**Environment**     NOC_FM_KEEP_EVENTS_WITH_ALARM
**Default Value**   -1
==================  =============================


.. _config-fm-alarm_close_retries:

alarm_close_retries
~~~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       fm.alarm_close_retries
**Key-Value Path**  fm/alarm_close_retries
**Environment**     NOC_FM_ALARM_CLOSE_RETRIES
**Default Value**   5
==================  ==========================


.. _config-fm-outage_refresh:

outage_refresh
~~~~~~~~~~~~~~

==================  =====================
**YAML Path**       fm.outage_refresh
**Key-Value Path**  fm/outage_refresh
**Environment**     NOC_FM_OUTAGE_REFRESH
**Default Value**   60s
==================  =====================


.. _config-fm-total_outage_refresh:

total_outage_refresh
~~~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       fm.total_outage_refresh
**Key-Value Path**  fm/total_outage_refresh
**Environment**     NOC_FM_TOTAL_OUTAGE_REFRESH
**Default Value**   60s
==================  ===========================

.. _config-fm-enable_rca_neighbor_cache:

enable_rca_neighbor_cache
~~~~~~~~~~~~~~~~~~~~~~~~~

==================  ================================
**YAML Path**       fm.enable_rca_neighbor_cache
**Key-Value Path**  fm/enable_rca_neighbor_cache
**Environment**     NOC_FM_ENABLE_RCA_NEIGHBOR_CACHE
**Default Value**   False
==================  ================================

Switch topology-based Root Cause Analysis from
traditional uplink-based to faster neighbor-cache implementation.
Preparations must be given before switching on.
See :ref:`release notes <release-19.3-rca-neighbor-cache>` for details.

.. versionadded:: 19.3

.. deprecated:: 20.1

    Will be deprecated and switched on by default in 20.1 generation
    of NOC releases

