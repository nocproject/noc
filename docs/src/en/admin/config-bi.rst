.. _config-bi:

bi
--


.. _config-bi-language:

language
~~~~~~~~

==================  ===============
**YAML Path**       bi.language
**Key-Value Path**  bi/language
**Environment**     NOC_BI_LANGUAGE
**Default Value**   en
==================  ===============


.. _config-bi-query_threads:

query_threads
~~~~~~~~~~~~~

==================  ====================
**YAML Path**       bi.query_threads
**Key-Value Path**  bi/query_threads
**Environment**     NOC_BI_QUERY_THREADS
**Default Value**   10
==================  ====================


.. _config-bi-extract_delay_alarms:

extract_delay_alarms
~~~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       bi.extract_delay_alarms
**Key-Value Path**  bi/extract_delay_alarms
**Environment**     NOC_BI_EXTRACT_DELAY_ALARMS
**Default Value**   1h
==================  ===========================


.. _config-bi-clean_delay_alarms:

clean_delay_alarms
~~~~~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       bi.clean_delay_alarms
**Key-Value Path**  bi/clean_delay_alarms
**Environment**     NOC_BI_CLEAN_DELAY_ALARMS
**Default Value**   1d
==================  =========================


.. _config-bi-reboot_interval:

reboot_interval
~~~~~~~~~~~~~~~

==================  ======================
**YAML Path**       bi.reboot_interval
**Key-Value Path**  bi/reboot_interval
**Environment**     NOC_BI_REBOOT_INTERVAL
**Default Value**   1M
==================  ======================


.. _config-bi-extract_delay_reboots:

extract_delay_reboots
~~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       bi.extract_delay_reboots
**Key-Value Path**  bi/extract_delay_reboots
**Environment**     NOC_BI_EXTRACT_DELAY_REBOOTS
**Default Value**   1h
==================  ============================


.. _config-bi-clean_delay_reboots:

clean_delay_reboots
~~~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       bi.clean_delay_reboots
**Key-Value Path**  bi/clean_delay_reboots
**Environment**     NOC_BI_CLEAN_DELAY_REBOOTS
**Default Value**   1d
==================  ==========================


.. _config-bi-chunk_size:

chunk_size
~~~~~~~~~~

==================  =================
**YAML Path**       bi.chunk_size
**Key-Value Path**  bi/chunk_size
**Environment**     NOC_BI_CHUNK_SIZE
**Default Value**   3000
==================  =================


.. _config-bi-extract_window:

extract_window
~~~~~~~~~~~~~~

==================  =====================
**YAML Path**       bi.extract_window
**Key-Value Path**  bi/extract_window
**Environment**     NOC_BI_EXTRACT_WINDOW
**Default Value**   1d
==================  =====================


.. _config-bi-enable_alarms:

enable_alarms
~~~~~~~~~~~~~

==================  ====================
**YAML Path**       bi.enable_alarms
**Key-Value Path**  bi/enable_alarms
**Environment**     NOC_BI_ENABLE_ALARMS
**Default Value**   False
==================  ====================


.. _config-bi-enable_reboots:

enable_reboots
~~~~~~~~~~~~~~

==================  =====================
**YAML Path**       bi.enable_reboots
**Key-Value Path**  bi/enable_reboots
**Environment**     NOC_BI_ENABLE_REBOOTS
**Default Value**   False
==================  =====================


.. _config-bi-enable_managedobjects:

enable_managedobjects
~~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       bi.enable_managedobjects
**Key-Value Path**  bi/enable_managedobjects
**Environment**     NOC_BI_ENABLE_MANAGEDOBJECTS
**Default Value**   False
==================  ============================


.. _config-bi-alarms_archive_policy:

alarms_archive_policy
~~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       bi.alarms_archive_policy
**Key-Value Path**  bi/alarms_archive_policy
**Environment**     NOC_BI_ALARMS_ARCHIVE_POLICY
**Default Value**   "weekly"
==================  ============================

Possible values:

* "weekly"
* "monthly"
* "quarterly"
* "yearly"


.. _config-bi-alarms_archive_batch_limit:

alarms_archive_batch_limit
~~~~~~~~~~~~~~~~~~~~~~~~~~

==================  =================================
**YAML Path**       bi.alarms_archive_batch_limit
**Key-Value Path**  bi/alarms_archive_batch_limit
**Environment**     NOC_BI_ALARMS_ARCHIVE_BATCH_LIMIT
**Default Value**   10000
==================  =================================


