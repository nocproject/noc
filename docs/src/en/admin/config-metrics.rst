.. _config-metrics:

metrics
-------
Internal metrics configuration


.. _config-metrics-default_hist:

default_hist
~~~~~~~~~~~~

==================  =============================================
**YAML Path**       metrics.default_hist
**Key-Value Path**  metrics/default_hist
**Environment**     NOC_METRICS_DEFAULT_HIST
**Default Value**   0.001, 0.005, 0.01, 0.05, 0.5, 1.0, 5.0, 10.0
==================  =============================================

Default histogram buckets (in seconds)

.. _config-metrics-enable_mongo_hist:

enable_mongo_hist
~~~~~~~~~~~~~~~~~

==================  =============================================
**YAML Path**       metrics.enable_mongo_hist
**Key-Value Path**  metrics/enable_mongo_hist
**Environment**     NOC_METRICS_ENABLE_MONGO_HIST
**Default Value**   False
==================  =============================================

Enable histograms for mongo transactions

.. _config-metrics-mongo_hist:

mongo_hist
~~~~~~~~~~

==================  =============================================
**YAML Path**       metrics.mongo_hist
**Key-Value Path**  metrics/mongo_hist
**Environment**     NOC_METRICS_MONGO_HIST
**Default Value**   0.001, 0.005, 0.01, 0.05, 0.5, 1.0, 5.0, 10.0
==================  =============================================

Histogram buckets (in seconds) for mongo transactions

.. _config-metrics-enable_postgres_hist:

enable_postgres_hist
~~~~~~~~~~~~~~~~~~~~

==================  =============================================
**YAML Path**       metrics.enable_mongo_hist
**Key-Value Path**  metrics/enable_mongo_hist
**Environment**     NOC_METRICS_ENABLE_POSTGRES_HIST
**Default Value**   False
==================  =============================================

Enable histograms for mongo postgresql transactions

.. _config-metrics-postgres_hist:

postgres_hist
~~~~~~~~~~~~~

==================  =============================================
**YAML Path**       metrics.postgres_hist
**Key-Value Path**  metrics/postgres_hist
**Environment**     NOC_METRICS_POSTGRES_HIST
**Default Value**   0.001, 0.005, 0.01, 0.05, 0.5, 1.0, 5.0, 10.0
==================  =============================================

Histogram buckets (in seconds) for postgresql transactions

.. _config-metrics-default_quantiles:

default_quantiles
~~~~~~~~~~~~~~~~~

==================  =============================================
**YAML Path**       metrics.default_quantiles
**Key-Value Path**  metrics/default_quantiles
**Environment**     NOC_METRICS_DEFAULT_QUANTILES
**Default Value**   0.5, 0.9, 0.95
==================  =============================================

Default quantiles to report

.. _config-metrics-default_quantiles_epsilon:

default_quantiles_epsilon
~~~~~~~~~~~~~~~~~~~~~~~~~

==================  =============================================
**YAML Path**       metrics.default_quantiles_epsilon
**Key-Value Path**  metrics/default_quantiles_epsilon
**Environment**     NOC_METRICS_DEFAULT_QUANTILES_EPSILON
**Default Value**   0.01
==================  =============================================

Acceptable ranking error for approximate quantiles calculation.

Consider we have 1000 measurements and calculating 2-nd quartile (50% or 0.5).
Exact quantile calculation must return `1000 * 0.5 = 500` item
of ordered list of measurement but we need to keep all 1000 measurements
in memory.

Approximate quantiles calculation guaranted to return an item between
`1000 * (0,5 - Epsilon)` and `1000 * (0.5 + Epsilon). So for default
value of 0.01 value between `490` and `510` position will be returned,
greatly relaxing memory requirements.

Lesser values means greater precision and greater memory and cpu requirements,
while greater values means lesser precision but lesser memory and cpu penalty.

.. _config-metrics-default_quantiles_window:

default_quantiles_window
~~~~~~~~~~~~~~~~~~~~~~~~

==================  =============================================
**YAML Path**       metrics.default_quantiles_window
**Key-Value Path**  metrics/default_quantiles_window
**Environment**     NOC_METRICS_DEFAULT_QUANTILES_WINDOW
**Default Value**   60
==================  =============================================

Quantiles window size in seconds. NOC maintains 2 quantile windows -
temporary and active one, purging active and swapping windows
every `default_quantiles_window` seconds.

.. _config-metrics-enable_mongo_quantiles:

enable_mongo_quantiles
~~~~~~~~~~~~~~~~~~~~~~

==================  =============================================
**YAML Path**       metrics.enable_mongo_quantiles
**Key-Value Path**  metrics/enable_mongo_quantiles
**Environment**     NOC_METRICS_ENABLE_MONGO_QUANTILES
**Default Value**   False
==================  =============================================

Enable quantiles collection for mongo transactions

.. _config-metrics-enable_postgres_quantiles:

enable_postgres_quantiles
~~~~~~~~~~~~~~~~~~~~~~~~~

==================  =============================================
**YAML Path**       metrics.enable_postgres_quantiles
**Key-Value Path**  metrics/enable_postgres_quantiles
**Environment**     NOC_METRICS_ENABLE_POSTGRES_QUANTILES
**Default Value**   False
==================  =============================================

Enable quantiles collection for postgresql transactions

