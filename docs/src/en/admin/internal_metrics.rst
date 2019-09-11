.. _admin-internal-metrics:

====================
NOC Internal Metrics
====================


.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 2
    :class: singlecol


.. internal-metrics-service-metrics:

Service Metrics
---------------

Given to a separate service for reference to the link /mon/

All metrics are tagged:

* service - the name of the service. It is fixed in the code
* pool - in the case of a sharded service, an indication of the pool


.. internal-metrics-general-service-metrics:

General Service Metrics
~~~~~~~~~~~~~~~~~~~~~~~

+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| Metric name   | Tag value                 | A place                                                 | Physical meaning                                                                     |
+===============+===========================+=========================================================+======================================================================================+
| service       | x                         | Service (core.service.base)                             | Service name                                                                         |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| status        | x                         |                                                         | Service status - always returns True                                                 |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| pid           | x                         |                                                         | Service process number                                                               |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| pool          | x                         |                                                         | The name of the pool with which the service works                                    |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| node          | x                         |                                                         | The server name is filled in config.node                                             |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| uptime        | x                         |                                                         | Time since the service started (in seconds)                                          |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| mon_requests  | x                         |                                                         | Number of requests by reference /mon/                                                |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| http_requests | method (GET / POST / PUT) | The number of calls to HTTP service                     |                                                                                      |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| http_response | status                    | Number of responses returned by the service (by status) |                                                                                      |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| spans         | x                         | spans                                                   | The number of requests for the return of telemetry to the service                    |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| errors        | x                         | debug                                                   | The number of traces in the service                                                  |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| unique_errors | x                         | debug                                                   | The number of unique (new) errors in the service (counted from the moment of launch) |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+
| err_<code>    | x                         | error                                                   | The number of errors by code                                                         |
+---------------+---------------------------+---------------------------------------------------------+--------------------------------------------------------------------------------------+


.. internal-metrics-cache-metrics:

Cache metrics
~~~~~~~~~~~~~

Most services provide work with the cache.
A separate component is responsible for this.
The cache is divided into 2 types:

*  internal (L1, internal) cache is represented by intra-service memory for a certain number of pieces of information
*  external ( L2, external) cache is organized by the cache service specified in the system settings. It can be located:

   *  mongodb (by default, unless otherwise specified)
   *  memcached - external service memcached
   *  redis - external service redis

Each element of the system that uses the cache is assigned a unique key - cache_key. It is used as tag.

+----------------------+-----------------------+--------------+-----------------------------------------------------------+
| Metric name          | Tag value             | A place      | Physical meaning                                          |
+======================+=======================+==============+===========================================================+
| cache_requests       | cache_key             | cachedmethod | The number of requests to the cache by key                |
+----------------------+-----------------------+--------------+-----------------------------------------------------------+
| cache_hits           | cache_key             | cachedmethod | The number of successful requests (hits) in the cache     |
+----------------------+-----------------------+--------------+-----------------------------------------------------------+
| cache_hits           | cache_level: internal | cachedmethod | Number of queries processed (passed) by internal cache    |
+----------------------+-----------------------+--------------+-----------------------------------------------------------+
| cache_hits           | cache_level: external | cachedmethod | Number of queries processed (passed) by external cache    |
+----------------------+-----------------------+--------------+-----------------------------------------------------------+
| cache_misses         | cache_key             | cachedmethod | The number of requests past the cache (missed)            |
+----------------------+-----------------------+--------------+-----------------------------------------------------------+
| cache_locks_acquires | cache_key             | cachedmethod | Number of cache accesses                                  |
+----------------------+-----------------------+--------------+-----------------------------------------------------------+


.. internal-metrics-http-client-metrics:

HTTP client metrics
~~~~~~~~~~~~~~~~~~~

Built-in HTTP client supports metrics:

+---------------------------+----------------------+-------------------+-------------------------------------------+
| Metric name               | Tag value            | A place           | Physical meaning                          |
+===========================+======================+===================+===========================================+
| httpclient_requests       | method (method name) | http_client.fetch | Number of completed requests              |
+---------------------------+----------------------+-------------------+-------------------------------------------+
| httpclient_timeouts       | x                    | http_client.fetch | Number of requests with an error timeout  |
+---------------------------+----------------------+-------------------+-------------------------------------------+
| httpclient_proxy_timeouts | x                    | http_client.fetch | The number of requests with a proxy error |
+---------------------------+----------------------+-------------------+-------------------------------------------+


.. internal-metrics-client-rpc-metrics:

Client RPC Metrics
~~~~~~~~~~~~~~~~~~

A client RPC used to interact with a part of system services that support the protocol JSON-RPC.
Supports the following tags:

* called_service - the name of the called service
* method - the name of the called method in the service (the list depends on the called service)

+-------------+-------------------------------------------------------------------------+-------------------+-------------------------------------------------------------+
| Metric name | Tag value                                                               | A place           | Physical meaning                                            |
+=============+=========================================================================+===================+=============================================================+
| rpc_call    | method (method name), called_service (name of the service being called) | http_client.fetch | The number of calls to a specific method in a given service |
+-------------+-------------------------------------------------------------------------+-------------------+-------------------------------------------------------------+


.. internal-metrics-nsq-client-metrics:

NSQ client metrics
~~~~~~~~~~~~~~~~~~

The client is used to work with the service queue - NSQD.
Used for two options:

* Subscription ( subscribe) on topic ( topic). For new messages
* Sending ( pub, publich) new messages in the topic ( topic)

The client provides the following metrics:

+-----------------------------+-----------------------------------------+-------------------+-----------------------------------------------------------------+
| Metric name                 | Tag value                               | A place           | Physical meaning                                                |
+=============================+=========================================+===================+=================================================================+
| nsq_msg_in_<topic>          | x                                       | Service.subscribe | Number of received (from topic) messages                        |
+-----------------------------+-----------------------------------------+-------------------+-----------------------------------------------------------------+
| nsq_msg_decode_fail_<topic> | x                                       | Service.subscribe | The number of received messages when decoding an error occurred |
+-----------------------------+-----------------------------------------+-------------------+-----------------------------------------------------------------+
| nsq_msg_processed_<topic>   | x                                       | Service.subscribe | The number of processed messages                                |
+-----------------------------+-----------------------------------------+-------------------+-----------------------------------------------------------------+
| nsq_msg_deferred_<topic>    | x                                       | Service.subscribe |                                                                 |
+-----------------------------+-----------------------------------------+-------------------+-----------------------------------------------------------------+
| error                       | type:nsqlookupd_query_error_code_<code> | reader            | Error when accessing HTTPLookupD                                |
+-----------------------------+-----------------------------------------+-------------------+-----------------------------------------------------------------+
| error                       | type:nsqlookupd_invalid_json_<code>     | reader            | Error decoding a message received from HTTPLookupD              |
+-----------------------------+-----------------------------------------+-------------------+-----------------------------------------------------------------+

.. internal-metrics-nsq-topicqueue-metrics:

NSQ TopicQueue metrics
~~~~~~~~~~~~~~~~~~~~~~

TopicQueue is the service's internal buffering queue between NSQ
message producing threads and the NSQ publisher.

The TopicQueue provides following metrics:

+-----------------------+----------------+------------+------------------------------------------------------------------------------------+
| Metric Name           | Tag value      | A place    | Physical meaning                                                                   |
+=======================+================+============+====================================================================================+
| nsq_msg_put           | `topic:<name>` | TopicQueue | Amount of messages submitted to TopicQueue                                         |
+-----------------------+----------------+------------+------------------------------------------------------------------------------------+
| nsq_msg_put_size      | `topic:<name>` | TopicQueue | Total size of messages submitted to TopicQueue (in octets)                         |
+-----------------------+----------------+------------+------------------------------------------------------------------------------------+
| nsq_msg_get           | `topic:<name>` | TopicQueue | Amount of messages fetched from TopicQueue                                         |
+-----------------------+----------------+------------+------------------------------------------------------------------------------------+
| nsq_msg_get_size      | `topic:<name>` | TopicQueue | Total size of messages fetched from TopicQueue (in octets)                         |
+-----------------------+----------------+------------+------------------------------------------------------------------------------------+
| nsq_msg_requeued      | `topic:<name>` | TopicQueue | Amount of messages returned to TopicQueue due to publishing errors                 |
+-----------------------+----------------+------------+------------------------------------------------------------------------------------+
| nsq_msg_requeued_size | `topic:<name>` | TopicQueue | Total size of messages returned to TopicQueue due to publishing errors (in octets) |
+-----------------------+----------------+------------+------------------------------------------------------------------------------------+

.. internal-metrics-dcs-metrics:

DCS metrics
~~~~~~~~~~~

DCS client is used to work with the services service Consul.
Consul is used for:

* Search services. A request is made to search for a service by name, the IP address is returned: the port of the nearest service
* To register yourself (at startup)
* For unregistration (at a stop)
* For blocking (if the launched service can work in a single copy)
* To get a slot (in the case of sharding by objects)

The client provides the following metrics:

+-----------------------------+----------------------------+--------------+-------------------------------------------------------+
| Metric name                 | Tag value                  | A place      | Physical meaning                                      |
+=============================+============================+==============+=======================================================+
| dcs_resolver_activeservices | name (service name)        | ResolverBase | Request for exhibiting active service.                |
+-----------------------------+----------------------------+--------------+-------------------------------------------------------+
| dcs_resolver_requests       | x                          | ResolverBase | The total number of requests for the nearest service  |
+-----------------------------+----------------------------+--------------+-------------------------------------------------------+
| dcs_resolver_hints          | x                          | ResolverBase |                                                       |
+-----------------------------+----------------------------+--------------+-------------------------------------------------------+
| dcs_resolver_success        | x                          | ResolverBase | The number of requests for service, completed success |
+-----------------------------+----------------------------+--------------+-------------------------------------------------------+
| errors                      | type: dcs_resolver_timeout | ResolverBase | The number of service requests that failed            |
+-----------------------------+----------------------------+--------------+-------------------------------------------------------+


.. internal-metrics-threadpool-metrics:

Threadpool metrics
~~~~~~~~~~~~~~~~~~

In system services using multi-thread processing is used pool of threads( threadpool).
This component is responsible for managing flows and provides the following metrics:

+---------------------------+-----------+--------------------+---------------------------------------+
| Metric name               | Tag value | A place            | Physical meaning                      |
+===========================+===========+====================+=======================================+
| <th_name>_max_workers     | x         | ThreadPoolExecutor | Maximum number of threads             |
+---------------------------+-----------+--------------------+---------------------------------------+
| <th_name>_idle_workers    | x         | ThreadPoolExecutor | Number of idle threads                |
+---------------------------+-----------+--------------------+---------------------------------------+
| <th_name>_running_workers | x         | ThreadPoolExecutor | The number of busy threads            |
+---------------------------+-----------+--------------------+---------------------------------------+
| <th_name>_submitted_tasks | x         | ThreadPoolExecutor | Number of completed tasks             |
+---------------------------+-----------+--------------------+---------------------------------------+
| <th_name>_queued_jobs     | x         | ThreadPoolExecutor | Number of jobs waiting (in the queue) |
+---------------------------+-----------+--------------------+---------------------------------------+
| <th_name>_uptime          | x         | ThreadPoolExecutor | Flow time                             |
+---------------------------+-----------+--------------------+---------------------------------------+

* <th_name> - The name of the threadpool. The following items are available:

   * script - used by the Activator service to run scripts
   * query - used by the service BI
   * max - use services Web,NBI


.. internal-metrics-scheduler-metrics:

Scheduler metrics
~~~~~~~~~~~~~~~~~

In system services using work with tasks, the scheduler component ( scheduler) is used.
It is responsible for working with tasks (planning, sending for execution ...).
Provides the following metrics:

+---------------------------------+-----------+-----------+------------------------------------------------------------+
| Metric name                     | Tag value | A place   | Physical meaning                                           |
+=================================+===========+===========+============================================================+
| <service>_jobs_started          | x         | Scheduler | The total number of running tasks (during operation)       |
+---------------------------------+-----------+-----------+------------------------------------------------------------+
| <service>_jobs_retries_exceeded | x         | Scheduler | Number of tasks exceeding the maximum number of executions |
+---------------------------------+-----------+-----------+------------------------------------------------------------+
| <service>_jobs_burst            | x         | Scheduler | The number of tasks exceeding the maximum                  |
+---------------------------------+-----------+-----------+------------------------------------------------------------+
| <service>_bulk_failed           | x         | Scheduler | The number of update status errors in the collection       |
+---------------------------------+-----------+-----------+------------------------------------------------------------+
| <service>_cache_set_requests    | x         | Scheduler | Number of Scheduler Cache Saves                            |
+---------------------------------+-----------+-----------+------------------------------------------------------------+
| <service>_cache_set_errors      | x         | Scheduler | The number of errors while saving the scheduler cache      |
+---------------------------------+-----------+-----------+------------------------------------------------------------+


.. internal-metrics-activator:

Activator
~~~~~~~~~

+-------------+------------------------+---------------------------+---------------------------------------------------------+
| Metric name | Tag value              | A place                   | Physical meaning                                        |
+=============+========================+===========================+=========================================================+
| error       | type:invalid_script    | ActivatorAPI.script       | The number of calls to a non-existent script            |
+-------------+------------------------+---------------------------+---------------------------------------------------------+
|             | type:script_error      | ActivatorAPI.script       | The number of errors during the execution of the script |
+-------------+------------------------+---------------------------+---------------------------------------------------------+
|             | type:snmp_v1_error     | ActivatorAPI.snmp_v1_get  | The number of SNMP V1 request errors                    |
+-------------+------------------------+---------------------------+---------------------------------------------------------+
|             | type:snmp_v2_error     | ActivatorAPI.snmp_v2c_get | Number of SNMP V2 Request Errors                        |
+-------------+------------------------+---------------------------+---------------------------------------------------------+
|             | type:http_error_<code> | ActivatorAPI.http_get     | The number of HTTP request errors (divided by code)     |
+-------------+------------------------+---------------------------+---------------------------------------------------------+


.. internal-metrics-discovery:

Discovery
~~~~~~~~~

todo


.. internal-metrics-sae:

SAE
~~~

todo


.. internal-metrics-ping:

Ping
~~~~

+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| Metric name               | Tag value | A place         | Physical meaning                                                            |
+===========================+===========+=================+=============================================================================+
| ignorable_ping_errors     | x         | PingSocket.ping | The number of ignored errors when the collector receives an ICMP message    |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_recvfrom_errors      | x         | PingSocket.ping | The number of errors when the collector receives an ICMP message            |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_unknown_icmp_packets | x         | PingSocket.ping | ICMP packet belonging to another service                                    |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_time_stepbacks       | x         | PingSocket.ping | The number of packages containing more time system                          |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_check_recover        | x         | PingSocket.ping | Number of IP address availability recoveries                                |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_objects              | x         | Pingservice     | The number of objects checked by the sample                                 |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| down_objects              | x         | Pingservice     | Number of unavailable objects                                               |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_probe_create         | x         | Pingservice     | Number of samples (one object = one sample)                                 |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_probe_update         | x         | Pingservice     | The number of updates in the samples                                        |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_probe_delete         | x         | Pingservice     | Number of samples removed                                                   |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_check_total          | x         | Pingservice     | The number of checks performed                                              |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_check_skips          | x         | Pingservice     | The number of missed checks                                                 |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_check_success        | x         | Pingservice     | The number of successful checks                                             |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+
| ping_check_fail           | x         | Pingservice     | The number of failed checks                                                 |
+---------------------------+-----------+-----------------+-----------------------------------------------------------------------------+


.. internal-metrics-collectors:

Collectors
~~~~~~~~~~

+-----------------+--------------------------+--------------------------------------------------------------------------+---------------------------------------------------------+
| Metric name     | Tag value                | A place                                                                  | Physical meaning                                        |
+=================+==========================+==========================================================================+=========================================================+
| trap_msg_in     | x                        | TrapServer.on_read                                                       | The number of incoming UPD SNMP Trap packets            |
+-----------------+--------------------------+--------------------------------------------------------------------------+---------------------------------------------------------+
| events_out      | x                        | TrapCollectorService.register_message                                    | The number of events in the direction of the classifier |
+-----------------+--------------------------+--------------------------------------------------------------------------+---------------------------------------------------------+
| sources_changed | x                        | TrapCollectorService.update_source, SyslogCollectorService.update_source | Updating information on source IP addresses             |
+-----------------+--------------------------+--------------------------------------------------------------------------+---------------------------------------------------------+
| sources_deleted | x                        | TrapCollectorService.sources_deleted, SyslogCollectorService             | Deleting information by IP address                      |
+-----------------+--------------------------+--------------------------------------------------------------------------+---------------------------------------------------------+
| error           | type:decode_failed       | TrapServer.on_read                                                       |                                                         |
+-----------------+--------------------------+--------------------------------------------------------------------------+---------------------------------------------------------+
| error           | type:socket_listen_error | on_activate                                                              |                                                         |
+-----------------+--------------------------+--------------------------------------------------------------------------+---------------------------------------------------------+
| error           | type:object_not_found    | TrapCollectorService.lookup_config                                       |                                                         |
+-----------------+--------------------------+--------------------------------------------------------------------------+---------------------------------------------------------+
| syslog_msg_in   | x                        | SyslogServer.on_read                                                     | The number of incoming UPD syslog packages              |
+-----------------+--------------------------+--------------------------------------------------------------------------+---------------------------------------------------------+


.. internal-metrics-classifier:

Classifier
~~~~~~~~~~

+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| Metric name           | Tag value | A place                    | Physical meaning                                                                 |
+=======================+===========+============================+==================================================================================+
| lag_us                | x         | ClassifierService.on_event | Delay versus message creation time at source                                     |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_preprocessed   | x         | ClassifierService          | The number of events classified by pre-processing                                |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_processed      | x         | ClassifierService          | The number of events received for processing                                     |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_unk_object     | x         | ClassifierService          | The number of events from an unknown object                                      |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_unk_duplicated | x         | ClassifierService          | Number of duplicate events detected by *codebook*                                |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_duplicated     | x         | ClassifierService          | The number of classified events that have a duplicate detected.                  |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_disposed       | x         | ClassifierService          | The number of classified events sent to the correlator                           |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_classified     | x         | ClassifierService          | The number of classified events (there was a match with the classification rule) |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_unknown        | x         | ClassifierService          | Number of unclassified (no rule found) events                                    |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_suppressed     | x         | ClassifierService          | Number of events suppressed due to replay                                        |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_deleted        | x         | ClassifierService          | Number of events deleted based on classification rule                            |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_failed         | x         | ClassifierService          | The number of events that fell under the preprocessing with an invalid class     |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_syslog         | x         | ClassifierService          | The number of events from the Syslog collector                                   |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_snmp_trap      | x         | ClassifierService          | The number of events from the SNMP Trap collector                                |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_system         | x         | ClassifierService          | The number of events from system services                                        |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| events_other          | x         | ClassifierService          | The number of events from unknown sources                                        |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| rules_checked         | x         | RuleSet.find_rule          | The number of checked rules                                                      |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+
| esm_lookups           | x         | XRuleLookup.lookup_rules   | The number of checked rules XRules                                               |
+-----------------------+-----------+----------------------------+----------------------------------------------------------------------------------+


.. internal-metrics-corellator:

Correlator
~~~~~~~~~~

+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| Metric name               | Tag value           | A place                               | Physical meaning                                                                                            |
+===========================+=====================+=======================================+=============================================================================================================+
| alarm_correlated_rule     | x                   | CorrelatorService.set_root_cause      | The number of accidents with the root cause                                                                 |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| alarm_change_mo           | x                   | CorrelatorService.raise_alarm         | Number of ManagedObject changes in crash with eval_expression                                               |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| alarm_reopen              | x                   | CorrelatorService.raise_alarm         | Number of reopen accidents                                                                                  |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| alarm_contribute          | x                   | CorrelatorService.raise_alarm         | The number of events involved in accidents                                                                  |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| alarm_raise               | x                   | CorrelatorService.raise_alarm         | Number of alarms raised                                                                                     |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| alarm_drop                | x                   | CorrelatorService.correlate           | Chilo missed accidents (executed if the handler returned Severity 0)                                        |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| unknown_object            | x                   | CorrelatorService.clear_alarm         | Number of failed crash closures due to lack of ManagedObject                                                |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| alarm_clear               | x                   | CorrelatorService.clear_alarm         | Number of closed accidents                                                                                  |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| alarm_dispose             | x                   | CorrelatorService.dispose_worker      | The number of received events                                                                               |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| alarm_dispose_error       | x                   | CorrelatorService.dispose_worker      | The number of errors when processing received events                                                        |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| event_lookup_failed       | x                   | CorrelatorService.lookup_event        | The number of errors when searching for events by ID                                                        |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| event_lookups             | x                   | CorrelatorService.dispose_worker      | The number of searches for events in the database by ID                                                     |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| event_hints               | x                   | CorrelatorService.get_event_from_hint | Number of use of information on the event from the message                                                  |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| alarm_correlated_topology | x                   | CorrelatorService.topology_rca        | The number of primed causes                                                                                 |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| detached_root             | x                   | check.check_close_consequence         | The number of trips of the root cause (in case of closing the main accident and the remaining subordinates) |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+
| errors                    | type: alarm_handler | CorrelatorService.correlate           | Runtime Handler Errors                                                                                      |
+---------------------------+---------------------+---------------------------------------+-------------------------------------------------------------------------------------------------------------+


.. internal-metrics-escalator:

Escalator
~~~~~~~~~

+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| Metric name                       | Tag value | A place                | Physical meaning                                                                                                                                   |
+===================================+===========+========================+====================================================================================================================================================+
| escalation_missed_alarm           | x         | escalator.escalate     | At the time of the escalation, the accident was removed.                                                                                           |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_already_closed         | x         | escalator.escalate     | At the time of the escalation, the accident was closed                                                                                             |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_alarm_is_not_root      | x         | escalator.escalate     | At the time of the escalation, the root cause of the accident was exposed (in this case, the accident is escalated as part of the parent)          |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_not_found              | x         | escalator.escalate     | Escalation was removed (checked during escalation)                                                                                                 |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_throttled              | x         | escalator.escalate     | The escalation was stopped because triggered check for exceeding the escalation limit                                                              |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_stop_on_maintenance    | x         | escalator.escalate     | The escalation was stopped because equipment covered with Maintanance Window                                                                       |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_tt_retry               | x         | escalator.escalate     | During the creation of the TT (Incident, Trouble ticket) in the external system was detected Temporary Error, the escalation went to repeat later  |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_tt_create              | x         | escalator.escalate     | The number of generated incidents in the external system                                                                                           |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_tt_fail                | x         | escalator.escalate     | The number of errors when creating incidents in the external system                                                                                |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_tt_comment             | x         | escalator.escalate     | Number of comments added to events in the external system                                                                                          |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_tt_comment_fail        | x         | escalator.escalate     | The number of errors when commenting comments on the incidents in the external system                                                              |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_notify                 | x         | escalator.escalate     | The number of sent notifications                                                                                                                   |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_closed_while_escalated | x         | escalator.escalate     | Number of closed accidents detected during escalation                                                                                              |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_already_deescalated    | x         | escalator.notify_close | De-escalation (incident closing) for an accident has already been made                                                                             |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_tt_close               | x         | escalator.notify_close | The number of incidents closed in the external system                                                                                              |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_tt_close_retry         | x         | escalator.notify_close | The number of repetitions of closing incidents in the external system                                                                              |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| escalation_tt_close_fail          | x         | escalator.notify_close | The number of errors when closing incidents in the external system                                                                                 |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| maintenance_tt_create             | x         | escalator.maintenance  |                                                                                                                                                    |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| maintenance_tt_fail               | x         | escalator.maintenance  |                                                                                                                                                    |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| maintenance_tt_close              | x         | escalator.maintenance  |                                                                                                                                                    |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
| maintenance_tt_close_fail         | x         | escalator.maintenance  |                                                                                                                                                    |
+-----------------------------------+-----------+------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+


.. internal-metrics-mailsender:

Mailsender
~~~~~~~~~~

+---------------+------------------+-----------------------------+-----------------------------------------------------------------+
| Metric name   | Tag value        | A place                     | Physical meaning                                                |
+===============+==================+=============================+=================================================================+
| smtp_response | code (SMTP code) | MailSenderService.send_mail | Number of sent messages (divided by SMTP server response codes) |
+---------------+------------------+-----------------------------+-----------------------------------------------------------------+


System-wide metrics (self-monitoring)
-------------------------------------

Subsystem metrics are calculated based on information from the database ( Postgres or MongoDB) and require an installed service seflmon.


.. internal-metrics-task:

Task
~~~~

In many services of the system, tasks are performed with time reference. It is responsible for this scheduler.
Technically, it is implemented as a queue of tasks in MongoDB.
Collection of tasks with which it works is called a template: noc.scheduler.<scheduler_name>.<shard>.
The tasks themselves are one-time and periodical. One-time after execution

Tags are added to all metrics:

* scheduler_name - name of the scheduler, usually the same as the name of the service
* pool - the name of the shard

+--------------------------------+----------------------+--------------+---------------------------------------------------------------------------------+
| Metric name                    | Tag value            | A place      | Physical meaning                                                                |
+================================+======================+==============+=================================================================================+
| task_pool_total                | scheduler_name, pool | selfmon.task | Total number of tasks                                                           |
+--------------------------------+----------------------+--------------+---------------------------------------------------------------------------------+
| task_exception_count           | -                    |              | Number of tasks with execution error                                            |
+--------------------------------+----------------------+--------------+---------------------------------------------------------------------------------+
| task_running_count             | -                    |              | The number of tasks in the state запущено                                       |
+--------------------------------+----------------------+--------------+---------------------------------------------------------------------------------+
| task_late_count                | -                    |              | The number of *delayed* tasks (start time later than the current)               |
+--------------------------------+----------------------+--------------+---------------------------------------------------------------------------------+
| task_lag_seconds               | -                    |              | In case of delayed tasks, the delay value of the task (in seconds)              |
+--------------------------------+----------------------+--------------+---------------------------------------------------------------------------------+
| task_box_time_avg_seconds      | -                    |              | Average task completion time (counted for equipment survey service (discovery)) |
+--------------------------------+----------------------+--------------+---------------------------------------------------------------------------------+
| task_periodic_time_avg_seconds | -                    |              | Average lead time                                                               |
+--------------------------------+----------------------+--------------+---------------------------------------------------------------------------------+


.. internal-metrics-inventory:

Inventory
~~~~~~~~~

+-----------------------------------+-----------+-----------------------+----------------------------------------------------------------------------------------------------------+
| Metric name                       | Tag value | A place               | Physical meaning                                                                                         |
+===================================+===========+=======================+==========================================================================================================+
| inventory_iface_count             | x         | selfmon.inventory     | The total number of interfaces in the system (calculated from the collection of inv.interfaces)          |
+-----------------------------------+-----------+-----------------------+----------------------------------------------------------------------------------------------------------+
| inventory_iface_physical_count    | x         |                       | The total number of physical interfaces in the system (calculated from the collection of inv.interfaces) |
+-----------------------------------+-----------+-----------------------+----------------------------------------------------------------------------------------------------------+
| inventory_link_count              | x         |                       | Total number of links in the system (calculated from the inv.links collection)                           |
+-----------------------------------+-----------+-----------------------+----------------------------------------------------------------------------------------------------------+
| inventory_subinterface_count      | x         |                       | Total number of subinterfaces in the system (calculated from the collection of inv.interfaces)           |
+-----------------------------------+-----------+-----------------------+----------------------------------------------------------------------------------------------------------+
| inventory_managedobject_total     | x         | selfmon.managedobject |                                                                                                          |
+-----------------------------------+-----------+-----------------------+----------------------------------------------------------------------------------------------------------+
| inventory_managedobject_managed   | x         |                       | The total number of management objects (ManagedObject) in the active state (ticked is_managed)           |
+-----------------------------------+-----------+-----------------------+----------------------------------------------------------------------------------------------------------+
| inventory_managedobject_unmanaged | x         | selfmon.managedobject |                                                                                                          |
+-----------------------------------+-----------+-----------------------+----------------------------------------------------------------------------------------------------------+

.. internal-metrics-fm:

FM
~~

For part of the metrics tags are added:

* ac_group - group of accidents. Present:

  * availablility- NOC | Managed Object | Ping FailedICMP accessibility crashes
  * discovery- System crashes (class Discovery | ..) generated by survey issues
  * other - The rest of the accident (Syslog / SNMP Trap)

* pool - a pool of services which practiced an accident (this includes pinger, classifier, correlator)
* shard - analogue of the pool for the external system

+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Metric name                             | Tag value      | A place    | Physical meaning                                                                                                                                                                 |
+=========================================+================+============+==================================================================================================================================================================================+
| fm_events_active_total                  | x              | selfmon.fm | The total number of active events (calculated from the fm.events.active collection)                                                                                              |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_events_active_last_lag_seconds       | x              | selfmon.fm | The difference (in seconds) between the current time and the time of the last message creation (counted according to the fm.events.active collection)                            |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_alarms_active_total                  | x              | selfmon.fm | The total number of active alarms (calculated from the fm.alarms.active collection)                                                                                              |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_alarms_archived_total                | x              | selfmon.fm | The total number of archived accidents (counted in the fm.alarms.archived collection)                                                                                            |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_alarms_active_last_lag_seconds       | x              | selfmon.fm | The difference (in seconds) between the current time and the time of the last crash creation (calculated from the fm.alarms.active collection)                                   |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_alarms_active_late_count             | x              | selfmon.fm | The number of events due to equipment unavailability (class NOC | Managed Object | Ping Failed) for which the class accident was not created NOC | Managed Object | Ping Failed. |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_alarms_active_pool_count             | ac_group, pool | selfmon.fm | Number of active alarms with splitting in pool and class                                                                                                                         |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_alarms_active_withroot_pool_count    | ac_group, pool | selfmon.fm | The number of active accidents with the underlying cause with splitting into pool and class                                                                                      |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_alarms_active_withoutroot_pool_count | ac_group, pool | selfmon.fm | Number of active accidents without root cause with splitting by pool and class                                                                                                   |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_escalation_pool_count                | shard          | selfmon.fm | The number of escalations in the queue                                                                                                                                           |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_escalation_first_lag_seconds         | shard          | selfmon.fm | The difference (in seconds) between the current time and the time of the first escalation in the queue                                                                           |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| fm_escalation_lag_seconds               | shard          | selfmon.fm | The difference (in seconds) between the current time and the time of the last escalation in the queue                                                                            |
+-----------------------------------------+----------------+------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

For each of the groups of metrics there are settings in the section config.selfmon:

* enable_managedobject - enable metrics collection by managedobject
* managedobject_ttl - metrics update interval for managedobject

Similar settings are for each section:

* enable_task
* task_ttl
* enable_inventory
* inventory_ttl
* enable_fm
* fm_ttl
