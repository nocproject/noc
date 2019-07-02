.. _config-ping:

ping
----


.. _config-ping-throttle_threshold:

throttle_threshold
~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       ping.throttle_threshold
**Key-Value Path**  ping/throttle_threshold
**Environment**     NOC_PING_THROTTLE_THRESHOLD
**Default Value**   FloatParameter()
==================  ===========================


.. _config-ping-restore_threshold:

restore_threshold
~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       ping.restore_threshold
**Key-Value Path**  ping/restore_threshold
**Environment**     NOC_PING_RESTORE_THRESHOLD
**Default Value**   FloatParameter()
==================  ==========================


.. _config-ping-tos:

tos
~~~

==================  =======================================
**YAML Path**       ping.tos
**Key-Value Path**  ping/tos
**Environment**     NOC_PING_TOS
**Default Value**   0
==================  =======================================

Possible values:

* min = 0
* max = 255


.. _config-ping-send_buffer:

send_buffer
~~~~~~~~~~~

Recommended send buffer size, 4M by default

==================  ====================
**YAML Path**       ping.send_buffer
**Key-Value Path**  ping/send_buffer
**Environment**     NOC_PING_SEND_BUFFER
**Default Value**   4 * 1048576
==================  ====================


.. _config-ping-receive_buffer:

receive_buffer
~~~~~~~~~~~~~~

Recommended receive buffer size, 4M by default

==================  =======================
**YAML Path**       ping.receive_buffer
**Key-Value Path**  ping/receive_buffer
**Environment**     NOC_PING_RECEIVE_BUFFER
**Default Value**   4 * 1048576
==================  =======================


.. _config-ping-ds_limit:

ds_limit
~~~~~~~~

DataStream request limit

==================  =================
**YAML Path**       ping.ds_limit
**Key-Value Path**  ping/ds_limit
**Environment**     NOC_PING_DS_LIMIT
**Default Value**   1000
==================  =================


