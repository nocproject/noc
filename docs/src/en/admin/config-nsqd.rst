.. _config-nsqd:

nsqd
----


.. _config-nsqd-addresses:

addresses
~~~~~~~~~

==================  =========================================================================
**YAML Path**       nsqd.addresses
**Key-Value Path**  nsqd/addresses
**Environment**     NOC_NSQD_ADDRESSES
**Default Value**   ServiceParameter(service='nsqd', wait=True, near=True, full_result=False)
==================  =========================================================================


.. _config-nsqd-http_addresses:

http_addresses
~~~~~~~~~~~~~~

==================  =============================================================================
**YAML Path**       nsqd.http_addresses
**Key-Value Path**  nsqd/http_addresses
**Environment**     NOC_NSQD_HTTP_ADDRESSES
**Default Value**   ServiceParameter(service='nsqdhttp', wait=True, near=True, full_result=False)
==================  =============================================================================


.. _config-nsqd-pub_retry_delay:

pub_retry_delay
~~~~~~~~~~~~~~~

==================  ========================
**YAML Path**       nsqd.pub_retry_delay
**Key-Value Path**  nsqd/pub_retry_delay
**Environment**     NOC_NSQD_PUB_RETRY_DELAY
**Default Value**   0.1
==================  ========================


.. _config-nsqd-ch_chunk_size:

ch_chunk_size
~~~~~~~~~~~~~

==================  ======================
**YAML Path**       nsqd.ch_chunk_size
**Key-Value Path**  nsqd/ch_chunk_size
**Environment**     NOC_NSQD_CH_CHUNK_SIZE
**Default Value**   4000
==================  ======================


.. _config-nsqd-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ========================
**YAML Path**       nsqd.connect_timeout
**Key-Value Path**  nsqd/connect_timeout
**Environment**     NOC_NSQD_CONNECT_TIMEOUT
**Default Value**   3s
==================  ========================


.. _config-nsqd-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ========================
**YAML Path**       nsqd.request_timeout
**Key-Value Path**  nsqd/request_timeout
**Environment**     NOC_NSQD_REQUEST_TIMEOUT
**Default Value**   30s
==================  ========================


.. _config-nsqd-reconnect_interval:

reconnect_interval
~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       nsqd.reconnect_interval
**Key-Value Path**  nsqd/reconnect_interval
**Environment**     NOC_NSQD_RECONNECT_INTERVAL
**Default Value**   15
==================  ===========================


.. _config-nsqd-compression:

compression
~~~~~~~~~~~

==================  ====================
**YAML Path**       nsqd.compression
**Key-Value Path**  nsqd/compression
**Environment**     NOC_NSQD_COMPRESSION
**Default Value**
==================  ====================

Possible values:

*
* deflate
* snappy


.. _config-nsqd-compression_level:

compression_level
~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       nsqd.compression_level
**Key-Value Path**  nsqd/compression_level
**Environment**     NOC_NSQD_COMPRESSION_LEVEL
**Default Value**   6
==================  ==========================


.. _config-nsqd-max_in_flight:

max_in_flight
~~~~~~~~~~~~~

==================  ======================
**YAML Path**       nsqd.max_in_flight
**Key-Value Path**  nsqd/max_in_flight
**Environment**     NOC_NSQD_MAX_IN_FLIGHT
**Default Value**   1
==================  ======================


