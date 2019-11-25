.. _config-syslogcollector:

syslogcollector
---------------


.. _config-syslogcollector-listen:

listen
~~~~~~

==================  ==========================
**YAML Path**       syslogcollector.listen
**Key-Value Path**  syslogcollector/listen
**Environment**     NOC_SYSLOGCOLLECTOR_LISTEN
**Default Value**   0.0.0.0:514
==================  ==========================


.. _config-syslogcollector-enable_reuseport:

enable_reuseport
~~~~~~~~~~~~~~~~

==================  ====================================
**YAML Path**       syslogcollector.enable_reuseport
**Key-Value Path**  syslogcollector/enable_reuseport
**Environment**     NOC_SYSLOGCOLLECTOR_ENABLE_REUSEPORT
**Default Value**   True
==================  ====================================


.. _config-syslogcollector-enable_freebind:

enable_freebind
~~~~~~~~~~~~~~~

==================  ===================================
**YAML Path**       syslogcollector.enable_freebind
**Key-Value Path**  syslogcollector/enable_freebind
**Environment**     NOC_SYSLOGCOLLECTOR_ENABLE_FREEBIND
**Default Value**   False
==================  ===================================


.. _config-syslogcollector-ds_limit:

ds_limit
~~~~~~~~

DataStream request limit

==================  ============================
**YAML Path**       syslogcollector.ds_limit
**Key-Value Path**  syslogcollector/ds_limit
**Environment**     NOC_SYSLOGCOLLECTOR_DS_LIMIT
**Default Value**   1000
==================  ============================


tgsender
--------


.. _config-tgsender-token:

token
~~~~~

==================  ==================
**YAML Path**       tgsender.token
**Key-Value Path**  tgsender/token
**Environment**     NOC_TGSENDER_TOKEN
**Default Value**   SecretParameter()
==================  ==================


.. _config-tgsender-retry_timeout:

retry_timeout
~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       tgsender.retry_timeout
**Key-Value Path**  tgsender/retry_timeout
**Environment**     NOC_TGSENDER_RETRY_TIMEOUT
**Default Value**   2
==================  ==========================


.. _config-tgsender-use_proxy:

use_proxy
~~~~~~~~~

==================  ======================
**YAML Path**       tgsender.use_proxy
**Key-Value Path**  tgsender/use_proxy
**Environment**     NOC_TGSENDER_USE_PROXY
**Default Value**   False
==================  ======================

icqsender
--------


.. _config-icqsender-token:

token
~~~~~

==================  ==================
**YAML Path**       icqsender.token
**Key-Value Path**  icqsender/token
**Environment**     NOC_ICQSENDER_TOKEN
**Default Value**   SecretParameter()
==================  ==================


.. _config-icqsender-retry_timeout:

retry_timeout
~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       icqsender.retry_timeout
**Key-Value Path**  icqsender/retry_timeout
**Environment**     NOC_ICQSENDER_RETRY_TIMEOUT
**Default Value**   2
==================  ==========================



