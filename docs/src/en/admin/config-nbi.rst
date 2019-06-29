.. _config-nbi:

nbi
---

:ref:`nbi<services-nbi>` service configuration

.. _config-nbi-max_threads:

max_threads
~~~~~~~~~~~

==================  =======================
**YAML Path**       nbi.max_threads
**Key-Value Path**  nbi/max_threads
**Environment**     NOC_NBI_MAX_THREADS
**Default Value**   10
==================  =======================

NBI process' threadpool size. Roughly - amount of concurrent
requests can be served by single :ref:`nbi<services-nbi>` instance.

.. _config-nbi-objectmetrics_max_interval:

objectmetrics_max_interval
~~~~~~~~~~~~~~~~~~~~~~~~~~

==================  ===================================
**YAML Path**       nbi.objectmetrics_max_interval
**Key-Value Path**  nbi/objectmetrics_max_interval
**Environment**     NOC_NBI_objectmetrics_max_interval
**Default Value**   3h
==================  ===================================

Maximal time span (in seconds) which can be requested via
:ref:`NBI objectmetrics API<api-nbi-objectmetrics>`.

