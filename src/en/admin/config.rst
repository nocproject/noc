.. _admin-config:

=======================
Configuration Reference
=======================


.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol


.. _config-Config:

Global
------

Global settings applicable to all services

.. _config-loglevel:

loglevel
~~~~~~~~

==================  ===================
**YAML Path**       loglevel
**Key-Value Path**  loglevel
**Environment**     NOC_LOGLEVEL
**Default Value**   info
==================  ===================

Possible values:

* critical
* error
* warning
* info
* debug

.. _config-brand:

brand
~~~~~

==================  =========
**YAML Path**       brand
**Key-Value Path**  brand
**Environment**     NOC_BRAND
**Default Value**   NOC
==================  =========


.. _config-global_n_instances:

global_n_instances
~~~~~~~~~~~~~~~~~~

==================  ======================
**YAML Path**       global_n_instances
**Key-Value Path**  global_n_instances
**Environment**     NOC_GLOBAL_N_INSTANCES
**Default Value**   1
==================  ======================


.. _config-installation_name:

installation_name
~~~~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       installation_name
**Key-Value Path**  installation_name
**Environment**     NOC_INSTALLATION_NAME
**Default Value**   Unconfigured installation
==================  =========================


.. _config-instance:

instance
~~~~~~~~

==================  ============
**YAML Path**       instance
**Key-Value Path**  instance
**Environment**     NOC_INSTANCE
**Default Value**   0
==================  ============


.. _config-language:

language
~~~~~~~~

==================  ============
**YAML Path**       language
**Key-Value Path**  language
**Environment**     NOC_LANGUAGE
**Default Value**   en
==================  ============


.. _config-language_code:

language_code
~~~~~~~~~~~~~

==================  =================
**YAML Path**       language_code
**Key-Value Path**  language_code
**Environment**     NOC_LANGUAGE_CODE
**Default Value**   en-us
==================  =================


.. _config-listen:

listen
~~~~~~

==================  ==========
**YAML Path**       listen
**Key-Value Path**  listen
**Environment**     NOC_LISTEN
**Default Value**   auto:0
==================  ==========


.. _config-log_format:

log_format
~~~~~~~~~~

==================  ==================================
**YAML Path**       log_format
**Key-Value Path**  log_format
**Environment**     NOC_LOG_FORMAT
**Default Value**   %(asctime)s [%(name)s] %(message)s
==================  ==================================


.. _config-thread_stack_size:

thread_stack_size
~~~~~~~~~~~~~~~~~

==================  =====================
**YAML Path**       thread_stack_size
**Key-Value Path**  thread_stack_size
**Environment**     NOC_THREAD_STACK_SIZE
**Default Value**   0
==================  =====================


.. _config-node:

node
~~~~

==================  ====================
**YAML Path**       node
**Key-Value Path**  node
**Environment**     NOC_NODE
**Default Value**   *host name*
==================  ====================


.. _config-pool:

pool
~~~~

==================  ==============================
**YAML Path**       pool
**Key-Value Path**  pool
**Environment**     NOC_POOL
**Default Value**
==================  ==============================


.. _config-secret_key:

secret_key
~~~~~~~~~~

==================  ==============
**YAML Path**       secret_key
**Key-Value Path**  secret_key
**Environment**     NOC_SECRET_KEY
**Default Value**   12345
==================  ==============


.. _config-timezone:

timezone
~~~~~~~~

==================  =============
**YAML Path**       timezone
**Key-Value Path**  timezone
**Environment**     NOC_TIMEZONE
**Default Value**   Europe/Moscow
==================  =============


.. _config-activator:

activator
---------


.. _config-activator-tos:

tos
~~~

==================  =======================================
**YAML Path**       activator.tos
**Key-Value Path**  activator/tos
**Environment**     NOC_ACTIVATOR_TOS
**Default Value**   0
==================  =======================================

Possible values:

* min=0
* max=255


.. _config-activator-script_threads:

script_threads
~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       activator.script_threads
**Key-Value Path**  activator/script_threads
**Environment**     NOC_ACTIVATOR_SCRIPT_THREADS
**Default Value**   10
==================  ============================


.. _config-activator-buffer_size:

buffer_size
~~~~~~~~~~~

==================  =========================
**YAML Path**       activator.buffer_size
**Key-Value Path**  activator/buffer_size
**Environment**     NOC_ACTIVATOR_BUFFER_SIZE
**Default Value**   1048576
==================  =========================


.. _config-activator-connect_retries:

connect_retries
~~~~~~~~~~~~~~~

retries on immediate disconnect

==================  =============================
**YAML Path**       activator.connect_retries
**Key-Value Path**  activator/connect_retries
**Environment**     NOC_ACTIVATOR_CONNECT_RETRIES
**Default Value**   3
==================  =============================


.. _config-activator-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

timeout after immediate disconnect

==================  =============================
**YAML Path**       activator.connect_timeout
**Key-Value Path**  activator/connect_timeout
**Environment**     NOC_ACTIVATOR_CONNECT_TIMEOUT
**Default Value**   3
==================  =============================


.. _config-activator-http_connect_timeout:

http_connect_timeout
~~~~~~~~~~~~~~~~~~~~

==================  ==================================
**YAML Path**       activator.http_connect_timeout
**Key-Value Path**  activator/http_connect_timeout
**Environment**     NOC_ACTIVATOR_HTTP_CONNECT_TIMEOUT
**Default Value**   20
==================  ==================================


.. _config-activator-http_request_timeout:

http_request_timeout
~~~~~~~~~~~~~~~~~~~~

==================  ==================================
**YAML Path**       activator.http_request_timeout
**Key-Value Path**  activator/http_request_timeout
**Environment**     NOC_ACTIVATOR_HTTP_REQUEST_TIMEOUT
**Default Value**   30
==================  ==================================


.. _config-activator-http_validate_cert:

http_validate_cert
~~~~~~~~~~~~~~~~~~

==================  ================================
**YAML Path**       activator.http_validate_cert
**Key-Value Path**  activator/http_validate_cert
**Environment**     NOC_ACTIVATOR_HTTP_VALIDATE_CERT
**Default Value**   False
==================  ================================


.. _config-audit:

audit
-----


.. _config-audit-command_ttl:

command_ttl
~~~~~~~~~~~

==================  =====================
**YAML Path**       audit.command_ttl
**Key-Value Path**  audit/command_ttl
**Environment**     NOC_AUDIT_COMMAND_TTL
**Default Value**   1m
==================  =====================


.. _config-audit-login_ttl:

login_ttl
~~~~~~~~~

==================  ===================
**YAML Path**       audit.login_ttl
**Key-Value Path**  audit/login_ttl
**Environment**     NOC_AUDIT_LOGIN_TTL
**Default Value**   1m
==================  ===================


.. _config-audit-reboot_ttl:

reboot_ttl
~~~~~~~~~~

==================  ====================
**YAML Path**       audit.reboot_ttl
**Key-Value Path**  audit/reboot_ttl
**Environment**     NOC_AUDIT_REBOOT_TTL
**Default Value**   0
==================  ====================


.. _config-audit-config_ttl:

config_ttl
~~~~~~~~~~

==================  ====================
**YAML Path**       audit.config_ttl
**Key-Value Path**  audit/config_ttl
**Environment**     NOC_AUDIT_CONFIG_TTL
**Default Value**   1y
==================  ====================


.. _config-audit-db_ttl:

db_ttl
~~~~~~

==================  ================
**YAML Path**       audit.db_ttl
**Key-Value Path**  audit/db_ttl
**Environment**     NOC_AUDIT_DB_TTL
**Default Value**   5y
==================  ================


.. _config-audit-config_changed_ttl:

config_changed_ttl
~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       audit.config_changed_ttl
**Key-Value Path**  audit/config_changed_ttl
**Environment**     NOC_AUDIT_CONFIG_CHANGED_TTL
**Default Value**   1y
==================  ============================


.. _config-backup:

backup
------


.. _config-backup-keep_days:

keep_days
~~~~~~~~~

==================  ====================
**YAML Path**       backup.keep_days
**Key-Value Path**  backup/keep_days
**Environment**     NOC_BACKUP_KEEP_DAYS
**Default Value**   14d
==================  ====================


.. _config-backup-keep_weeks:

keep_weeks
~~~~~~~~~~

==================  =====================
**YAML Path**       backup.keep_weeks
**Key-Value Path**  backup/keep_weeks
**Environment**     NOC_BACKUP_KEEP_WEEKS
**Default Value**   12w
==================  =====================


.. _config-backup-keep_day_of_week:

keep_day_of_week
~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       backup.keep_day_of_week
**Key-Value Path**  backup/keep_day_of_week
**Environment**     NOC_BACKUP_KEEP_DAY_OF_WEEK
**Default Value**   6
==================  ===========================


.. _config-backup-keep_months:

keep_months
~~~~~~~~~~~

==================  ======================
**YAML Path**       backup.keep_months
**Key-Value Path**  backup/keep_months
**Environment**     NOC_BACKUP_KEEP_MONTHS
**Default Value**   12
==================  ======================


.. _config-backup-keep_day_of_month:

keep_day_of_month
~~~~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       backup.keep_day_of_month
**Key-Value Path**  backup/keep_day_of_month
**Environment**     NOC_BACKUP_KEEP_DAY_OF_MONTH
**Default Value**   1
==================  ============================


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


.. _config-cache:

cache
-----


.. _config-cache-vcinterfacescount:

vcinterfacescount
~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       cache.vcinterfacescount
**Key-Value Path**  cache/vcinterfacescount
**Environment**     NOC_CACHE_VCINTERFACESCOUNT
**Default Value**   1h
==================  ===========================


.. _config-cache-vcprefixes:

vcprefixes
~~~~~~~~~~

==================  ====================
**YAML Path**       cache.vcprefixes
**Key-Value Path**  cache/vcprefixes
**Environment**     NOC_CACHE_VCPREFIXES
**Default Value**   1h
==================  ====================


.. _config-cache-cache_class:

cache_class
~~~~~~~~~~~

==================  ===============================
**YAML Path**       cache.cache_class
**Key-Value Path**  cache/cache_class
**Environment**     NOC_CACHE_CACHE_CLASS
**Default Value**   noc.core.cache.mongo.MongoCache
==================  ===============================


.. _config-cache-default_ttl:

default_ttl
~~~~~~~~~~~

==================  =====================
**YAML Path**       cache.default_ttl
**Key-Value Path**  cache/default_ttl
**Environment**     NOC_CACHE_DEFAULT_TTL
**Default Value**   1d
==================  =====================


.. _config-cache-pool_size:

pool_size
~~~~~~~~~

==================  ===================
**YAML Path**       cache.pool_size
**Key-Value Path**  cache/pool_size
**Environment**     NOC_CACHE_POOL_SIZE
**Default Value**   8
==================  ===================


.. _config-card:

card
----


.. _config-card-language:

language
~~~~~~~~

==================  =================
**YAML Path**       card.language
**Key-Value Path**  card/language
**Environment**     NOC_CARD_LANGUAGE
**Default Value**   en
==================  =================


.. _config-card-alarmheat_tooltip_limit:

alarmheat_tooltip_limit
~~~~~~~~~~~~~~~~~~~~~~~

==================  ================================
**YAML Path**       card.alarmheat_tooltip_limit
**Key-Value Path**  card/alarmheat_tooltip_limit
**Environment**     NOC_CARD_ALARMHEAT_TOOLTIP_LIMIT
**Default Value**   5
==================  ================================


.. _config-chwriter:

chwriter
--------


.. _config-chwriter-batch_size:

batch_size
~~~~~~~~~~

==================  =======================
**YAML Path**       chwriter.batch_size
**Key-Value Path**  chwriter/batch_size
**Environment**     NOC_CHWRITER_BATCH_SIZE
**Default Value**   50000
==================  =======================


.. _config-chwriter-records_buffer:

records_buffer
~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       chwriter.records_buffer
**Key-Value Path**  chwriter/records_buffer
**Environment**     NOC_CHWRITER_RECORDS_BUFFER
**Default Value**   1000000
==================  ===========================


.. _config-chwriter-batch_delay_ms:

batch_delay_ms
~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       chwriter.batch_delay_ms
**Key-Value Path**  chwriter/batch_delay_ms
**Environment**     NOC_CHWRITER_BATCH_DELAY_MS
**Default Value**   10000
==================  ===========================


.. _config-chwriter-channel_expire_interval:

channel_expire_interval
~~~~~~~~~~~~~~~~~~~~~~~

==================  ====================================
**YAML Path**       chwriter.channel_expire_interval
**Key-Value Path**  chwriter/channel_expire_interval
**Environment**     NOC_CHWRITER_CHANNEL_EXPIRE_INTERVAL
**Default Value**   5M
==================  ====================================


.. _config-chwriter-suspend_timeout_ms:

suspend_timeout_ms
~~~~~~~~~~~~~~~~~~

==================  ===============================
**YAML Path**       chwriter.suspend_timeout_ms
**Key-Value Path**  chwriter/suspend_timeout_ms
**Environment**     NOC_CHWRITER_SUSPEND_TIMEOUT_MS
**Default Value**   3000
==================  ===============================


.. _config-chwriter-topic:

topic
~~~~~

==================  ==================
**YAML Path**       chwriter.topic
**Key-Value Path**  chwriter/topic
**Environment**     NOC_CHWRITER_TOPIC
**Default Value**   chwriter
==================  ==================


.. _config-chwriter-write_to:

write_to
~~~~~~~~

==================  =====================
**YAML Path**       chwriter.write_to
**Key-Value Path**  chwriter/write_to
**Environment**     NOC_CHWRITER_WRITE_TO
**Default Value**   StringParameter()
==================  =====================


.. _config-chwriter-max_in_flight:

max_in_flight
~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       chwriter.max_in_flight
**Key-Value Path**  chwriter/max_in_flight
**Environment**     NOC_CHWRITER_MAX_IN_FLIGHT
**Default Value**   10
==================  ==========================


.. _config-classifier:

classifier
----------


.. _config-classifier-lookup_handler:

lookup_handler
~~~~~~~~~~~~~~

==================  =============================================
**YAML Path**       classifier.lookup_handler
**Key-Value Path**  classifier/lookup_handler
**Environment**     NOC_CLASSIFIER_LOOKUP_HANDLER
**Default Value**   noc.services.classifier.rulelookup.RuleLookup
==================  =============================================


.. _config-classifier-default_interface_profile:

default_interface_profile
~~~~~~~~~~~~~~~~~~~~~~~~~

==================  ========================================
**YAML Path**       classifier.default_interface_profile
**Key-Value Path**  classifier/default_interface_profile
**Environment**     NOC_CLASSIFIER_DEFAULT_INTERFACE_PROFILE
**Default Value**   default
==================  ========================================


.. _config-classifier-default_rule:

default_rule
~~~~~~~~~~~~

==================  ===========================
**YAML Path**       classifier.default_rule
**Key-Value Path**  classifier/default_rule
**Environment**     NOC_CLASSIFIER_DEFAULT_RULE
**Default Value**   Unknown | Default
==================  ===========================


.. _config-clickhouse:

clickhouse
----------


.. _config-clickhouse-rw_addresses:

rw_addresses
~~~~~~~~~~~~

==================  =================================================
**YAML Path**       clickhouse.rw_addresses
**Key-Value Path**  clickhouse/rw_addresses
**Environment**     NOC_CLICKHOUSE_RW_ADDRESSES
**Default Value**   ServiceParameter(service='clickhouse', wait=True)
==================  =================================================


.. _config-clickhouse-db:

db
--

==================  =================
**YAML Path**       clickhouse.db
**Key-Value Path**  clickhouse/db
**Environment**     NOC_CLICKHOUSE_DB
**Default Value**   noc
==================  =================


.. _config-clickhouse-rw_user:

rw_user
~~~~~~~

==================  ======================
**YAML Path**       clickhouse.rw_user
**Key-Value Path**  clickhouse/rw_user
**Environment**     NOC_CLICKHOUSE_RW_USER
**Default Value**   default
==================  ======================


.. _config-clickhouse-rw_password:

rw_password
~~~~~~~~~~~

==================  ==========================
**YAML Path**       clickhouse.rw_password
**Key-Value Path**  clickhouse/rw_password
**Environment**     NOC_CLICKHOUSE_RW_PASSWORD
**Default Value**   SecretParameter()
==================  ==========================


.. _config-clickhouse-ro_addresses:

ro_addresses
~~~~~~~~~~~~

==================  =================================================
**YAML Path**       clickhouse.ro_addresses
**Key-Value Path**  clickhouse/ro_addresses
**Environment**     NOC_CLICKHOUSE_RO_ADDRESSES
**Default Value**   ServiceParameter(service='clickhouse', wait=True)
==================  =================================================


.. _config-clickhouse-ro_user:

ro_user
~~~~~~~

==================  ======================
**YAML Path**       clickhouse.ro_user
**Key-Value Path**  clickhouse/ro_user
**Environment**     NOC_CLICKHOUSE_RO_USER
**Default Value**   readonly
==================  ======================


.. _config-clickhouse-ro_password:

ro_password
~~~~~~~~~~~

==================  ==========================
**YAML Path**       clickhouse.ro_password
**Key-Value Path**  clickhouse/ro_password
**Environment**     NOC_CLICKHOUSE_RO_PASSWORD
**Default Value**   SecretParameter()
==================  ==========================


.. _config-clickhouse-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ==============================
**YAML Path**       clickhouse.request_timeout
**Key-Value Path**  clickhouse/request_timeout
**Environment**     NOC_CLICKHOUSE_REQUEST_TIMEOUT
**Default Value**   1h
==================  ==============================


.. _config-clickhouse-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ==============================
**YAML Path**       clickhouse.connect_timeout
**Key-Value Path**  clickhouse/connect_timeout
**Environment**     NOC_CLICKHOUSE_CONNECT_TIMEOUT
**Default Value**   10s
==================  ==============================


.. _config-clickhouse-default_merge_tree_granularity:

default_merge_tree_granularity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

==================  =============================================
**YAML Path**       clickhouse.default_merge_tree_granularity
**Key-Value Path**  clickhouse/default_merge_tree_granularity
**Environment**     NOC_CLICKHOUSE_DEFAULT_MERGE_TREE_GRANULARITY
**Default Value**   8192
==================  =============================================


.. _config-clickhouse-encoding:

encoding
~~~~~~~~

==================  ===================================
**YAML Path**       clickhouse.encoding
**Key-Value Path**  clickhouse/encoding
**Environment**     NOC_CLICKHOUSE_ENCODING
**Default Value**
==================  ===================================

Possible values:

*
* deflate
* gzip

.. _config-clickhouse-cluster:

cluster
~~~~~~~

Cluster name for sharded/replicated configuration
Matches appropriative <remote_servers> part

==================  ======================
**YAML Path**       clickhouse.cluster
**Key-Value Path**  clickhouse/cluster
**Environment**     NOC_CLICKHOUSE_CLUSTER
**Default Value**   StringParameter()
==================  ======================


.. _config-clickhouse-cluster_topology:

cluster_topology
~~~~~~~~~~~~~~~~

==================  ===============================
**YAML Path**       clickhouse.cluster_topology
**Key-Value Path**  clickhouse/cluster_topology
**Environment**     NOC_CLICKHOUSE_CLUSTER_TOPOLOGY
**Default Value**   1
==================  ===============================

Examples:

+-------+----------------------------------------------------------------------------------+
| Value | Description                                                                      |
+=======+==================================================================================+
| 1     | non-replicated, non-sharded configuration                                        |
+-------+----------------------------------------------------------------------------------+
| 1,1   | 2 shards, non-replicated                                                         |
+-------+----------------------------------------------------------------------------------+
| 2,2   | 2 shards, 2 replicas in each                                                     |
+-------+----------------------------------------------------------------------------------+
| 3:2,2 | first shard has 2 replicas an weight 3, second shard has 2 replicas and weight 1 |
+-------+----------------------------------------------------------------------------------+


.. _config-cm:

cm
--


.. _config-cm-vcs_type:

vcs_type
~~~~~~~~

==================  ===========================================
**YAML Path**       cm.vcs_type
**Key-Value Path**  cm/vcs_type
**Environment**     NOC_CM_VCS_TYPE
**Default Value**   'gridvcs', choices=['hg', 'CVS', 'gridvcs']
==================  ===========================================


.. _config-consul:

consul
------


.. _config-consul-token:

token
~~~~~

==================  =================
**YAML Path**       consul.token
**Key-Value Path**  consul/token
**Environment**     NOC_CONSUL_TOKEN
**Default Value**   SecretParameter()
==================  =================


.. _config-consul-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       consul.connect_timeout
**Key-Value Path**  consul/connect_timeout
**Environment**     NOC_CONSUL_CONNECT_TIMEOUT
**Default Value**   5s
==================  ==========================


.. _config-consul-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       consul.request_timeout
**Key-Value Path**  consul/request_timeout
**Environment**     NOC_CONSUL_REQUEST_TIMEOUT
**Default Value**   1h
==================  ==========================


.. _config-consul-near_retry_timeout:

near_retry_timeout
~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       consul.near_retry_timeout
**Key-Value Path**  consul/near_retry_timeout
**Environment**     NOC_CONSUL_NEAR_RETRY_TIMEOUT
**Default Value**   1
==================  =============================


.. _config-consul-host:

host
~~~~

==================  ===============
**YAML Path**       consul.host
**Key-Value Path**  consul/host
**Environment**     NOC_CONSUL_HOST
**Default Value**   consul
==================  ===============


.. _config-consul-port:

port
~~~~

==================  ===============
**YAML Path**       consul.port
**Key-Value Path**  consul/port
**Environment**     NOC_CONSUL_PORT
**Default Value**   8500
==================  ===============


.. _config-consul-check_interval:

check_interval
~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       consul.check_interval
**Key-Value Path**  consul/check_interval
**Environment**     NOC_CONSUL_CHECK_INTERVAL
**Default Value**   10s
==================  =========================


.. _config-consul-check_timeout:

check_timeout
~~~~~~~~~~~~~

==================  ========================
**YAML Path**       consul.check_timeout
**Key-Value Path**  consul/check_timeout
**Environment**     NOC_CONSUL_CHECK_TIMEOUT
**Default Value**   1s
==================  ========================


.. _config-consul-release:

release
~~~~~~~

==================  ==================
**YAML Path**       consul.release
**Key-Value Path**  consul/release
**Environment**     NOC_CONSUL_RELEASE
**Default Value**   1M
==================  ==================


.. _config-consul-session_ttl:

session_ttl
~~~~~~~~~~~

==================  ======================
**YAML Path**       consul.session_ttl
**Key-Value Path**  consul/session_ttl
**Environment**     NOC_CONSUL_SESSION_TTL
**Default Value**   10s
==================  ======================


.. _config-consul-lock_delay:

lock_delay
~~~~~~~~~~

==================  =====================
**YAML Path**       consul.lock_delay
**Key-Value Path**  consul/lock_delay
**Environment**     NOC_CONSUL_LOCK_DELAY
**Default Value**   20s
==================  =====================


.. _config-consul-retry_timeout:

retry_timeout
~~~~~~~~~~~~~

==================  ========================
**YAML Path**       consul.retry_timeout
**Key-Value Path**  consul/retry_timeout
**Environment**     NOC_CONSUL_RETRY_TIMEOUT
**Default Value**   1s
==================  ========================


.. _config-consul-keepalive_attempts:

keepalive_attempts
~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       consul.keepalive_attempts
**Key-Value Path**  consul/keepalive_attempts
**Environment**     NOC_CONSUL_KEEPALIVE_ATTEMPTS
**Default Value**   5
==================  =============================


.. _config-consul-base:

base
~~~~

kv lookup base

==================  ===============
**YAML Path**       consul.base
**Key-Value Path**  consul/base
**Environment**     NOC_CONSUL_BASE
**Default Value**   noc
==================  ===============


.. _config-correlator:

correlator
----------


.. _config-correlator-max_threads:

max_threads
~~~~~~~~~~~

==================  ==========================
**YAML Path**       correlator.max_threads
**Key-Value Path**  correlator/max_threads
**Environment**     NOC_CORRELATOR_MAX_THREADS
**Default Value**   20
==================  ==========================


.. _config-correlator-topology_rca_window:

topology_rca_window
~~~~~~~~~~~~~~~~~~~

==================  ==================================
**YAML Path**       correlator.topology_rca_window
**Key-Value Path**  correlator/topology_rca_window
**Environment**     NOC_CORRELATOR_TOPOLOGY_RCA_WINDOW
**Default Value**   0
==================  ==================================


.. _config-correlator-oo_close_delay:

oo_close_delay
~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       correlator.oo_close_delay
**Key-Value Path**  correlator/oo_close_delay
**Environment**     NOC_CORRELATOR_OO_CLOSE_DELAY
**Default Value**   20s
==================  =============================


.. _config-correlator-discovery_delay:

discovery_delay
~~~~~~~~~~~~~~~

==================  ==============================
**YAML Path**       correlator.discovery_delay
**Key-Value Path**  correlator/discovery_delay
**Environment**     NOC_CORRELATOR_DISCOVERY_DELAY
**Default Value**   10M
==================  ==============================


.. _config-correlator-auto_escalation:

auto_escalation
~~~~~~~~~~~~~~~

==================  ==============================
**YAML Path**       correlator.auto_escalation
**Key-Value Path**  correlator/auto_escalation
**Environment**     NOC_CORRELATOR_AUTO_ESCALATION
**Default Value**   True
==================  ==============================


.. _config-customization:

customization
-------------


.. _config-customization-favicon_url:

favicon_url
~~~~~~~~~~~

==================  =====================================
**YAML Path**       customization.favicon_url
**Key-Value Path**  customization/favicon_url
**Environment**     NOC_CUSTOMIZATION_FAVICON_URL
**Default Value**   /static/img/logo_24x24_deep_azure.png
==================  =====================================


.. _config-customization-logo_url:

logo_url
~~~~~~~~

==================  ==========================
**YAML Path**       customization.logo_url
**Key-Value Path**  customization/logo_url
**Environment**     NOC_CUSTOMIZATION_LOGO_URL
**Default Value**   /static/img/logo_white.svg
==================  ==========================


.. _config-customization-logo_width:

logo_width
~~~~~~~~~~

==================  ============================
**YAML Path**       customization.logo_width
**Key-Value Path**  customization/logo_width
**Environment**     NOC_CUSTOMIZATION_LOGO_WIDTH
**Default Value**   24
==================  ============================


.. _config-customization-logo_height:

logo_height
~~~~~~~~~~~

==================  =============================
**YAML Path**       customization.logo_height
**Key-Value Path**  customization/logo_height
**Environment**     NOC_CUSTOMIZATION_LOGO_HEIGHT
**Default Value**   24
==================  =============================


.. _config-customization-branding_color:

branding_color
~~~~~~~~~~~~~~

==================  ================================
**YAML Path**       customization.branding_color
**Key-Value Path**  customization/branding_color
**Environment**     NOC_CUSTOMIZATION_BRANDING_COLOR
**Default Value**   #ffffff
==================  ================================


.. _config-customization-branding_background_color:

branding_background_color
~~~~~~~~~~~~~~~~~~~~~~~~~

==================  ===========================================
**YAML Path**       customization.branding_background_color
**Key-Value Path**  customization/branding_background_color
**Environment**     NOC_CUSTOMIZATION_BRANDING_BACKGROUND_COLOR
**Default Value**   #34495e
==================  ===========================================


.. _config-customization-preview_theme:

preview_theme
~~~~~~~~~~~~~

==================  ===============================
**YAML Path**       customization.preview_theme
**Key-Value Path**  customization/preview_theme
**Environment**     NOC_CUSTOMIZATION_PREVIEW_THEME
**Default Value**   midnight
==================  ===============================


.. _config-date_time_formats:

date_time_formats
-----------------


.. _config-date_time_formats-date_format:

date_format
~~~~~~~~~~~

==================  =================================
**YAML Path**       date_time_formats.date_format
**Key-Value Path**  date_time_formats/date_format
**Environment**     NOC_DATE_TIME_FORMATS_DATE_FORMAT
**Default Value**   d.m.Y
==================  =================================


.. _config-date_time_formats-datetime_format:

datetime_format
~~~~~~~~~~~~~~~

==================  =====================================
**YAML Path**       date_time_formats.datetime_format
**Key-Value Path**  date_time_formats/datetime_format
**Environment**     NOC_DATE_TIME_FORMATS_DATETIME_FORMAT
**Default Value**   d.m.Y H:i:s
==================  =====================================


.. _config-date_time_formats-month_day_format:

month_day_format
~~~~~~~~~~~~~~~~

==================  ======================================
**YAML Path**       date_time_formats.month_day_format
**Key-Value Path**  date_time_formats/month_day_format
**Environment**     NOC_DATE_TIME_FORMATS_MONTH_DAY_FORMAT
**Default Value**   F j
==================  ======================================


.. _config-date_time_formats-time_format:

time_format
~~~~~~~~~~~

==================  =================================
**YAML Path**       date_time_formats.time_format
**Key-Value Path**  date_time_formats/time_format
**Environment**     NOC_DATE_TIME_FORMATS_TIME_FORMAT
**Default Value**   H:i:s
==================  =================================


.. _config-date_time_formats-year_month_format:

year_month_format
~~~~~~~~~~~~~~~~~

==================  =======================================
**YAML Path**       date_time_formats.year_month_format
**Key-Value Path**  date_time_formats/year_month_format
**Environment**     NOC_DATE_TIME_FORMATS_YEAR_MONTH_FORMAT
**Default Value**   F Y
==================  =======================================


.. _config-dcs:

dcs
---


.. _config-dcs-resolution_timeout:

resolution_timeout
~~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       dcs.resolution_timeout
**Key-Value Path**  dcs/resolution_timeout
**Environment**     NOC_DCS_RESOLUTION_TIMEOUT
**Default Value**   5M
==================  ==========================


.. _config-discovery:

discovery
---------


.. _config-discovery-max_threads:

max_threads
~~~~~~~~~~~

==================  =========================
**YAML Path**       discovery.max_threads
**Key-Value Path**  discovery/max_threads
**Environment**     NOC_DISCOVERY_MAX_THREADS
**Default Value**   20
==================  =========================


.. _config-discovery-sample:

sample
~~~~~~

==================  ====================
**YAML Path**       discovery.sample
**Key-Value Path**  discovery/sample
**Environment**     NOC_DISCOVERY_SAMPLE
**Default Value**   0
==================  ====================


.. _config-dns:

dns
---


.. _config-dns-warn_before_expired:

warn_before_expired
~~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       dns.warn_before_expired
**Key-Value Path**  dns/warn_before_expired
**Environment**     NOC_DNS_WARN_BEFORE_EXPIRED
**Default Value**   30d
==================  ===========================


.. _config-escalator:

escalator
---------


.. _config-escalator-max_threads:

max_threads
~~~~~~~~~~~

==================  =========================
**YAML Path**       escalator.max_threads
**Key-Value Path**  escalator/max_threads
**Environment**     NOC_ESCALATOR_MAX_THREADS
**Default Value**   5
==================  =========================


.. _config-escalator-retry_timeout:

retry_timeout
~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       escalator.retry_timeout
**Key-Value Path**  escalator/retry_timeout
**Environment**     NOC_ESCALATOR_RETRY_TIMEOUT
**Default Value**   60s
==================  ===========================


.. _config-escalator-tt_escalation_limit:

tt_escalation_limit
~~~~~~~~~~~~~~~~~~~

==================  =================================
**YAML Path**       escalator.tt_escalation_limit
**Key-Value Path**  escalator/tt_escalation_limit
**Environment**     NOC_ESCALATOR_TT_ESCALATION_LIMIT
**Default Value**   10
==================  =================================


.. _config-escalator-ets:

ets
~~~

==================  =================
**YAML Path**       escalator.ets
**Key-Value Path**  escalator/ets
**Environment**     NOC_ESCALATOR_ETS
**Default Value**   60s
==================  =================


.. _config-escalator-wait_tt_check_interval:

wait_tt_check_interval
~~~~~~~~~~~~~~~~~~~~~~

==================  ====================================
**YAML Path**       escalator.wait_tt_check_interval
**Key-Value Path**  escalator/wait_tt_check_interval
**Environment**     NOC_ESCALATOR_WAIT_TT_CHECK_INTERVAL
**Default Value**   60s
==================  ====================================


.. _config-escalator-sample:

sample
~~~~~~

==================  ====================
**YAML Path**       escalator.sample
**Key-Value Path**  escalator/sample
**Environment**     NOC_ESCALATOR_SAMPLE
**Default Value**   0
==================  ====================


.. _config-features:

features
--------


.. _config-features-use_uvlib:

use_uvlib
~~~~~~~~~

==================  ======================
**YAML Path**       features.use_uvlib
**Key-Value Path**  features/use_uvlib
**Environment**     NOC_FEATURES_USE_UVLIB
**Default Value**   False
==================  ======================


.. _config-features-cp:

cp
--

==================  ===============
**YAML Path**       features.cp
**Key-Value Path**  features/cp
**Environment**     NOC_FEATURES_CP
**Default Value**   True
==================  ===============


.. _config-features-sentry:

sentry
~~~~~~

==================  ===================
**YAML Path**       features.sentry
**Key-Value Path**  features/sentry
**Environment**     NOC_FEATURES_SENTRY
**Default Value**   False
==================  ===================


.. _config-features-traefik:

traefik
~~~~~~~

==================  ====================
**YAML Path**       features.traefik
**Key-Value Path**  features/traefik
**Environment**     NOC_FEATURES_TRAEFIK
**Default Value**   False
==================  ====================


.. _config-features-cpclient:

cpclient
~~~~~~~~

==================  =====================
**YAML Path**       features.cpclient
**Key-Value Path**  features/cpclient
**Environment**     NOC_FEATURES_CPCLIENT
**Default Value**   False
==================  =====================


.. _config-features-telemetry:

telemetry
~~~~~~~~~

Enable internal telemetry export to Clickhouse

==================  ======================
**YAML Path**       features.telemetry
**Key-Value Path**  features/telemetry
**Environment**     NOC_FEATURES_TELEMETRY
**Default Value**   False
==================  ======================


.. _config-features-consul_healthchecks:

consul_healthchecks
~~~~~~~~~~~~~~~~~~~

While registering serive in consul also register health check

==================  ================================
**YAML Path**       features.consul_healthchecks
**Key-Value Path**  features/consul_healthchecks
**Environment**     NOC_FEATURES_CONSUL_HEALTHCHECKS
**Default Value**   True
==================  ================================


.. _config-features-service_registration:

service_registration
~~~~~~~~~~~~~~~~~~~~

Permit consul self registration

==================  =================================
**YAML Path**       features.service_registration
**Key-Value Path**  features/service_registration
**Environment**     NOC_FEATURES_SERVICE_REGISTRATION
**Default Value**   True
==================  =================================


.. _config-features-pypy:

pypy
~~~~

==================  =================
**YAML Path**       features.pypy
**Key-Value Path**  features/pypy
**Environment**     NOC_FEATURES_PYPY
**Default Value**   False
==================  =================


.. _config-features-forensic:

forensic
~~~~~~~~

==================  =====================
**YAML Path**       features.forensic
**Key-Value Path**  features/forensic
**Environment**     NOC_FEATURES_FORENSIC
**Default Value**   False
==================  =====================


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


.. _config-geocoding:

geocoding
---------


.. _config-geocoding-order:

order
~~~~~

==================  ===================
**YAML Path**       geocoding.order
**Key-Value Path**  geocoding/order
**Environment**     NOC_GEOCODING_ORDER
**Default Value**   yandex,google
==================  ===================


.. _config-geocoding-yandex_key:

yandex_key
~~~~~~~~~~

==================  ========================
**YAML Path**       geocoding.yandex_key
**Key-Value Path**  geocoding/yandex_key
**Environment**     NOC_GEOCODING_YANDEX_KEY
**Default Value**
==================  ========================


.. _config-geocoding-google_key:

google_key
~~~~~~~~~~

==================  ========================
**YAML Path**       geocoding.google_key
**Key-Value Path**  geocoding/google_key
**Environment**     NOC_GEOCODING_GOOGLE_KEY
**Default Value**
==================  ========================


.. _config-geocoding-google_language:

google_language
~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       geocoding.google_language
**Key-Value Path**  geocoding/google_language
**Environment**     NOC_GEOCODING_GOOGLE_LANGUAGE
**Default Value**   en
==================  =============================


.. _config-gis:

gis
---


.. _config-gis-ellipsoid:

ellipsoid
~~~~~~~~~

==================  =================
**YAML Path**       gis.ellipsoid
**Key-Value Path**  gis/ellipsoid
**Environment**     NOC_GIS_ELLIPSOID
**Default Value**   PZ-90
==================  =================


.. _config-gis-enable_osm:

enable_osm
~~~~~~~~~~

==================  ==================
**YAML Path**       gis.enable_osm
**Key-Value Path**  gis/enable_osm
**Environment**     NOC_GIS_ENABLE_OSM
**Default Value**   True
==================  ==================


.. _config-gis-enable_google_sat:

enable_google_sat
~~~~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       gis.enable_google_sat
**Key-Value Path**  gis/enable_google_sat
**Environment**     NOC_GIS_ENABLE_GOOGLE_SAT
**Default Value**   False
==================  =========================


.. _config-gis-enable_google_roadmap:

enable_google_roadmap
~~~~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       gis.enable_google_roadmap
**Key-Value Path**  gis/enable_google_roadmap
**Environment**     NOC_GIS_ENABLE_GOOGLE_ROADMAP
**Default Value**   False
==================  =============================


.. _config-gis-tile_size:

tile_size
~~~~~~~~~

Tile size 256x256

==================  =================
**YAML Path**       gis.tile_size
**Key-Value Path**  gis/tile_size
**Environment**     NOC_GIS_TILE_SIZE
**Default Value**   256
==================  =================


.. _config-gis-tilecache_padding:

tilecache_padding
~~~~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       gis.tilecache_padding
**Key-Value Path**  gis/tilecache_padding
**Environment**     NOC_GIS_TILECACHE_PADDING
**Default Value**   0
==================  =========================


.. _config-grafanads:

grafanads
---------


.. _config-grafanads-db_threads:

db_threads
~~~~~~~~~~

==================  ========================
**YAML Path**       grafanads.db_threads
**Key-Value Path**  grafanads/db_threads
**Environment**     NOC_GRAFANADS_DB_THREADS
**Default Value**   10
==================  ========================


.. _config-http_client:

http_client
-----------


.. _config-http_client-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ===============================
**YAML Path**       http_client.connect_timeout
**Key-Value Path**  http_client/connect_timeout
**Environment**     NOC_HTTP_CLIENT_CONNECT_TIMEOUT
**Default Value**   10s
==================  ===============================


.. _config-http_client-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ===============================
**YAML Path**       http_client.request_timeout
**Key-Value Path**  http_client/request_timeout
**Environment**     NOC_HTTP_CLIENT_REQUEST_TIMEOUT
**Default Value**   1h
==================  ===============================


.. _config-http_client-user_agent:

user_agent
~~~~~~~~~~

==================  ==========================
**YAML Path**       http_client.user_agent
**Key-Value Path**  http_client/user_agent
**Environment**     NOC_HTTP_CLIENT_USER_AGENT
**Default Value**   noc
==================  ==========================


.. _config-http_client-buffer_size:

buffer_size
~~~~~~~~~~~

==================  ===========================
**YAML Path**       http_client.buffer_size
**Key-Value Path**  http_client/buffer_size
**Environment**     NOC_HTTP_CLIENT_BUFFER_SIZE
**Default Value**   128 * 1024
==================  ===========================


.. _config-http_client-max_redirects:

max_redirects
~~~~~~~~~~~~~

==================  =============================
**YAML Path**       http_client.max_redirects
**Key-Value Path**  http_client/max_redirects
**Environment**     NOC_HTTP_CLIENT_MAX_REDIRECTS
**Default Value**   5
==================  =============================


.. _config-http_client-ns_cache_size:

ns_cache_size
~~~~~~~~~~~~~

==================  =============================
**YAML Path**       http_client.ns_cache_size
**Key-Value Path**  http_client/ns_cache_size
**Environment**     NOC_HTTP_CLIENT_NS_CACHE_SIZE
**Default Value**   1000
==================  =============================


.. _config-http_client-resolver_ttl:

resolver_ttl
~~~~~~~~~~~~

==================  ============================
**YAML Path**       http_client.resolver_ttl
**Key-Value Path**  http_client/resolver_ttl
**Environment**     NOC_HTTP_CLIENT_RESOLVER_TTL
**Default Value**   3s
==================  ============================


.. _config-http_client-http_port:

http_port
~~~~~~~~~

==================  =========================
**YAML Path**       http_client.http_port
**Key-Value Path**  http_client/http_port
**Environment**     NOC_HTTP_CLIENT_HTTP_PORT
**Default Value**   80
==================  =========================


.. _config-http_client-https_port:

https_port
~~~~~~~~~~

==================  ==========================
**YAML Path**       http_client.https_port
**Key-Value Path**  http_client/https_port
**Environment**     NOC_HTTP_CLIENT_HTTPS_PORT
**Default Value**   443
==================  ==========================


.. _config-http_client-validate_certs:

validate_certs
~~~~~~~~~~~~~~

Have to be set as True

==================  ==============================
**YAML Path**       http_client.validate_certs
**Key-Value Path**  http_client/validate_certs
**Environment**     NOC_HTTP_CLIENT_VALIDATE_CERTS
**Default Value**   False
==================  ==============================


.. _config-influxdb:

influxdb
--------


.. _config-influxdb-addresses:

addresses
~~~~~~~~~

==================  ===============================================
**YAML Path**       influxdb.addresses
**Key-Value Path**  influxdb/addresses
**Environment**     NOC_INFLUXDB_ADDRESSES
**Default Value**   ServiceParameter(service='influxdb', wait=True)
==================  ===============================================


.. _config-influxdb-db:

db
~~

==================  ===============
**YAML Path**       influxdb.db
**Key-Value Path**  influxdb/db
**Environment**     NOC_INFLUXDB_DB
**Default Value**   noc
==================  ===============


.. _config-influxdb-user:

user
~~~~

==================  =================
**YAML Path**       influxdb.user
**Key-Value Path**  influxdb/user
**Environment**     NOC_INFLUXDB_USER
**Default Value**   StringParameter()
==================  =================


.. _config-influxdb-password:

password
~~~~~~~~

==================  =====================
**YAML Path**       influxdb.password
**Key-Value Path**  influxdb/password
**Environment**     NOC_INFLUXDB_PASSWORD
**Default Value**   SecretParameter()
==================  =====================


.. _config-influxdb-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       influxdb.request_timeout
**Key-Value Path**  influxdb/request_timeout
**Environment**     NOC_INFLUXDB_REQUEST_TIMEOUT
**Default Value**   10M
==================  ============================


.. _config-influxdb-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       influxdb.connect_timeout
**Key-Value Path**  influxdb/connect_timeout
**Environment**     NOC_INFLUXDB_CONNECT_TIMEOUT
**Default Value**   10s
==================  ============================


.. _config-logging:

logging
-------


.. _config-logging-log_api_calls:

log_api_calls
~~~~~~~~~~~~~

==================  =========================
**YAML Path**       logging.log_api_calls
**Key-Value Path**  logging/log_api_calls
**Environment**     NOC_LOGGING_LOG_API_CALLS
**Default Value**   False
==================  =========================


.. _config-logging-log_sql_statements:

log_sql_statements
~~~~~~~~~~~~~~~~~~

==================  ==============================
**YAML Path**       logging.log_sql_statements
**Key-Value Path**  logging/log_sql_statements
**Environment**     NOC_LOGGING_LOG_SQL_STATEMENTS
**Default Value**   False
==================  ==============================


.. _config-login:

login
-----


.. _config-login-methods:

methods
~~~~~~~

==================  =================
**YAML Path**       login.methods
**Key-Value Path**  login/methods
**Environment**     NOC_LOGIN_METHODS
**Default Value**   local
==================  =================


.. _config-login-session_ttl:

session_ttl
~~~~~~~~~~~

==================  =====================
**YAML Path**       login.session_ttl
**Key-Value Path**  login/session_ttl
**Environment**     NOC_LOGIN_SESSION_TTL
**Default Value**   7d
==================  =====================


.. _config-login-language:

language
~~~~~~~~

==================  ==================
**YAML Path**       login.language
**Key-Value Path**  login/language
**Environment**     NOC_LOGIN_LANGUAGE
**Default Value**   en
==================  ==================


.. _config-login-restrict_to_group:

restrict_to_group
~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       login.restrict_to_group
**Key-Value Path**  login/restrict_to_group
**Environment**     NOC_LOGIN_RESTRICT_TO_GROUP
**Default Value**
==================  ===========================


.. _config-login-single_session_group:

single_session_group
~~~~~~~~~~~~~~~~~~~~

==================  ==============================
**YAML Path**       login.single_session_group
**Key-Value Path**  login/single_session_group
**Environment**     NOC_LOGIN_SINGLE_SESSION_GROUP
**Default Value**
==================  ==============================


.. _config-login-mutual_exclusive_group:

mutual_exclusive_group
~~~~~~~~~~~~~~~~~~~~~~

==================  ================================
**YAML Path**       login.mutual_exclusive_group
**Key-Value Path**  login/mutual_exclusive_group
**Environment**     NOC_LOGIN_MUTUAL_EXCLUSIVE_GROUP
**Default Value**
==================  ================================


.. _config-login-idle_timeout:

idle_timeout
~~~~~~~~~~~~

==================  ======================
**YAML Path**       login.idle_timeout
**Key-Value Path**  login/idle_timeout
**Environment**     NOC_LOGIN_IDLE_TIMEOUT
**Default Value**   1w
==================  ======================


.. _config-login-pam_service:

pam_service
~~~~~~~~~~~

==================  =====================
**YAML Path**       login.pam_service
**Key-Value Path**  login/pam_service
**Environment**     NOC_LOGIN_PAM_SERVICE
**Default Value**   noc
==================  =====================


.. _config-login-radius_secret:

radius_secret
~~~~~~~~~~~~~

==================  =======================
**YAML Path**       login.radius_secret
**Key-Value Path**  login/radius_secret
**Environment**     NOC_LOGIN_RADIUS_SECRET
**Default Value**   noc
==================  =======================


.. _config-login-radius_server:

radius_server
~~~~~~~~~~~~~

==================  =======================
**YAML Path**       login.radius_server
**Key-Value Path**  login/radius_server
**Environment**     NOC_LOGIN_RADIUS_SERVER
**Default Value**   StringParameter()
==================  =======================


.. _config-login-user_cookie_ttl:

user_cookie_ttl
~~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       login.user_cookie_ttl
**Key-Value Path**  login/user_cookie_ttl
**Environment**     NOC_LOGIN_USER_COOKIE_TTL
**Default Value**   1
==================  =========================


.. _config-mailsender:

mailsender
----------


.. _config-mailsender-smtp_server:

smtp_server
~~~~~~~~~~~

==================  ==========================
**YAML Path**       mailsender.smtp_server
**Key-Value Path**  mailsender/smtp_server
**Environment**     NOC_MAILSENDER_SMTP_SERVER
**Default Value**   StringParameter()
==================  ==========================


.. _config-mailsender-smtp_port:

smtp_port
~~~~~~~~~

==================  ========================
**YAML Path**       mailsender.smtp_port
**Key-Value Path**  mailsender/smtp_port
**Environment**     NOC_MAILSENDER_SMTP_PORT
**Default Value**   25
==================  ========================


.. _config-mailsender-use_tls:

use_tls
~~~~~~~

==================  ======================
**YAML Path**       mailsender.use_tls
**Key-Value Path**  mailsender/use_tls
**Environment**     NOC_MAILSENDER_USE_TLS
**Default Value**   False
==================  ======================


.. _config-mailsender-helo_hostname:

helo_hostname
~~~~~~~~~~~~~

==================  ============================
**YAML Path**       mailsender.helo_hostname
**Key-Value Path**  mailsender/helo_hostname
**Environment**     NOC_MAILSENDER_HELO_HOSTNAME
**Default Value**   noc
==================  ============================


.. _config-mailsender-from_address:

from_address
~~~~~~~~~~~~

==================  ===========================
**YAML Path**       mailsender.from_address
**Key-Value Path**  mailsender/from_address
**Environment**     NOC_MAILSENDER_FROM_ADDRESS
**Default Value**   noc@example.com
==================  ===========================


.. _config-mailsender-smtp_user:

smtp_user
~~~~~~~~~

==================  ========================
**YAML Path**       mailsender.smtp_user
**Key-Value Path**  mailsender/smtp_user
**Environment**     NOC_MAILSENDER_SMTP_USER
**Default Value**   StringParameter()
==================  ========================


.. _config-mailsender-smtp_password:

smtp_password
~~~~~~~~~~~~~

==================  ============================
**YAML Path**       mailsender.smtp_password
**Key-Value Path**  mailsender/smtp_password
**Environment**     NOC_MAILSENDER_SMTP_PASSWORD
**Default Value**   SecretParameter()
==================  ============================


.. _config-memcached:

memcached
---------


.. _config-memcached-addresses:

addresses
~~~~~~~~~

==================  ==================================================================
**YAML Path**       memcached.addresses
**Key-Value Path**  memcached/addresses
**Environment**     NOC_MEMCACHED_ADDRESSES
**Default Value**   ServiceParameter(service='memcached', wait=True, full_result=True)
==================  ==================================================================


.. _config-memcached-pool_size:

pool_size
~~~~~~~~~

==================  =======================
**YAML Path**       memcached.pool_size
**Key-Value Path**  memcached/pool_size
**Environment**     NOC_MEMCACHED_POOL_SIZE
**Default Value**   8
==================  =======================


.. _config-memcached-default_ttl:

default_ttl
~~~~~~~~~~~

==================  =========================
**YAML Path**       memcached.default_ttl
**Key-Value Path**  memcached/default_ttl
**Environment**     NOC_MEMCACHED_DEFAULT_TTL
**Default Value**   1d
==================  =========================


.. _config-mongo:

mongo
-----


.. _config-mongo-addresses:

addresses
~~~~~~~~~

==================  ============================================
**YAML Path**       mongo.addresses
**Key-Value Path**  mongo/addresses
**Environment**     NOC_MONGO_ADDRESSES
**Default Value**   ServiceParameter(service='mongo', wait=True)
==================  ============================================


.. _config-mongo-db:

db
~~

==================  ============
**YAML Path**       mongo.db
**Key-Value Path**  mongo/db
**Environment**     NOC_MONGO_DB
**Default Value**   noc
==================  ============


.. _config-mongo-user:

user
~~~~

==================  =================
**YAML Path**       mongo.user
**Key-Value Path**  mongo/user
**Environment**     NOC_MONGO_USER
**Default Value**   StringParameter()
==================  =================


.. _config-mongo-password:

password
~~~~~~~~

==================  ==================
**YAML Path**       mongo.password
**Key-Value Path**  mongo/password
**Environment**     NOC_MONGO_PASSWORD
**Default Value**   SecretParameter()
==================  ==================


.. _config-mongo-rs:

rs
~~

==================  =================
**YAML Path**       mongo.rs
**Key-Value Path**  mongo/rs
**Environment**     NOC_MONGO_RS
**Default Value**   StringParameter()
==================  =================


.. _config-mongo-retries:

retries
~~~~~~~

==================  =================
**YAML Path**       mongo.retries
**Key-Value Path**  mongo/retries
**Environment**     NOC_MONGO_RETRIES
**Default Value**   20
==================  =================


.. _config-mongo-timeout:

timeout
~~~~~~~

==================  =================
**YAML Path**       mongo.timeout
**Key-Value Path**  mongo/timeout
**Environment**     NOC_MONGO_TIMEOUT
**Default Value**   3s
==================  =================


.. _config-mrt:

mrt
---


.. _config-mrt-max_concurrency:

max_concurrency
~~~~~~~~~~~~~~~

==================  =======================
**YAML Path**       mrt.max_concurrency
**Key-Value Path**  mrt/max_concurrency
**Environment**     NOC_MRT_MAX_CONCURRENCY
**Default Value**   50
==================  =======================


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


.. _config-nsqlookupd:

nsqlookupd
----------


.. _config-nsqlookupd-addresses:

addresses
~~~~~~~~~

==================  ===============================================================================
**YAML Path**       nsqlookupd.addresses
**Key-Value Path**  nsqlookupd/addresses
**Environment**     NOC_NSQLOOKUPD_ADDRESSES
**Default Value**   ServiceParameter(service='nsqlookupd', wait=True, near=True, full_result=False)
==================  ===============================================================================


.. _config-nsqlookupd-http_addresses:

http_addresses
~~~~~~~~~~~~~~

==================  ========================================================================
**YAML Path**       nsqlookupd.http_addresses
**Key-Value Path**  nsqlookupd/http_addresses
**Environment**     NOC_NSQLOOKUPD_HTTP_ADDRESSES
**Default Value**   ServiceParameter(service='nsqlookupdhttp', wait=True, full_result=False)
==================  ========================================================================


.. _config-path:

path
----


.. _config-path-smilint:

smilint
~~~~~~~

==================  =================
**YAML Path**       path.smilint
**Key-Value Path**  path/smilint
**Environment**     NOC_PATH_SMILINT
**Default Value**   StringParameter()
==================  =================


.. _config-path-smidump:

smidump
~~~~~~~

==================  =================
**YAML Path**       path.smidump
**Key-Value Path**  path/smidump
**Environment**     NOC_PATH_SMIDUMP
**Default Value**   StringParameter()
==================  =================


.. _config-path-dig:

dig
~~~

==================  =================
**YAML Path**       path.dig
**Key-Value Path**  path/dig
**Environment**     NOC_PATH_DIG
**Default Value**   StringParameter()
==================  =================


.. _config-path-vcs_path:

vcs_path
~~~~~~~~

==================  =================
**YAML Path**       path.vcs_path
**Key-Value Path**  path/vcs_path
**Environment**     NOC_PATH_VCS_PATH
**Default Value**   /usr/local/bin/hg
==================  =================


.. _config-path-repo:

repo
~~~~

==================  =============
**YAML Path**       path.repo
**Key-Value Path**  path/repo
**Environment**     NOC_PATH_REPO
**Default Value**   /var/repo
==================  =============


.. _config-path-config_mirror_path:

config_mirror_path
~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       path.config_mirror_path
**Key-Value Path**  path/config_mirror_path
**Environment**     NOC_PATH_CONFIG_MIRROR_PATH
**Default Value**   StringParameter('')
==================  ===========================


.. _config-path-backup_dir:

backup_dir
~~~~~~~~~~

==================  ===================
**YAML Path**       path.backup_dir
**Key-Value Path**  path/backup_dir
**Environment**     NOC_PATH_BACKUP_DIR
**Default Value**   /var/backup
==================  ===================


.. _config-path-etl_import:

etl_import
~~~~~~~~~~

==================  ===================
**YAML Path**       path.etl_import
**Key-Value Path**  path/etl_import
**Environment**     NOC_PATH_ETL_IMPORT
**Default Value**   /var/lib/noc/import
==================  ===================


.. _config-path-ssh_key_prefix:

ssh_key_prefix
~~~~~~~~~~~~~~

==================  =======================
**YAML Path**       path.ssh_key_prefix
**Key-Value Path**  path/ssh_key_prefix
**Environment**     NOC_PATH_SSH_KEY_PREFIX
**Default Value**   etc/noc_ssh
==================  =======================


.. _config-path-beef_prefix:

beef_prefix
~~~~~~~~~~~

==================  ====================
**YAML Path**       path.beef_prefix
**Key-Value Path**  path/beef_prefix
**Environment**     NOC_PATH_BEEF_PREFIX
**Default Value**   /var/lib/noc/beef/sa
==================  ====================


.. _config-path-cp_new:

cp_new
~~~~~~

==================  =============================
**YAML Path**       path.cp_new
**Key-Value Path**  path/cp_new
**Environment**     NOC_PATH_CP_NEW
**Default Value**   /var/lib/noc/cp/crashinfo/new
==================  =============================


.. _config-path-bi_data_prefix:

bi_data_prefix
~~~~~~~~~~~~~~

==================  =======================
**YAML Path**       path.bi_data_prefix
**Key-Value Path**  path/bi_data_prefix
**Environment**     NOC_PATH_BI_DATA_PREFIX
**Default Value**   /var/lib/noc/bi
==================  =======================


.. _config-path-babel_cfg:

babel_cfg
~~~~~~~~~

==================  ==================
**YAML Path**       path.babel_cfg
**Key-Value Path**  path/babel_cfg
**Environment**     NOC_PATH_BABEL_CFG
**Default Value**   etc/babel.cfg
==================  ==================


.. _config-path-babel:

babel
~~~~~

==================  ==============
**YAML Path**       path.babel
**Key-Value Path**  path/babel
**Environment**     NOC_PATH_BABEL
**Default Value**   ./bin/pybabel
==================  ==============


.. _config-path-pojson:

pojson
~~~~~~

==================  ===============
**YAML Path**       path.pojson
**Key-Value Path**  path/pojson
**Environment**     NOC_PATH_POJSON
**Default Value**   ./bin/pojson
==================  ===============


.. _config-path-collection_fm_mibs:

collection_fm_mibs
~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       path.collection_fm_mibs
**Key-Value Path**  path/collection_fm_mibs
**Environment**     NOC_PATH_COLLECTION_FM_MIBS
**Default Value**   collections/fm.mibs/
==================  ===========================


.. _config-path-supervisor_cfg:

supervisor_cfg
~~~~~~~~~~~~~~

==================  =======================
**YAML Path**       path.supervisor_cfg
**Key-Value Path**  path/supervisor_cfg
**Environment**     NOC_PATH_SUPERVISOR_CFG
**Default Value**   etc/noc_services.conf
==================  =======================


.. _config-path-legacy_config:

legacy_config
~~~~~~~~~~~~~

==================  ======================
**YAML Path**       path.legacy_config
**Key-Value Path**  path/legacy_config
**Environment**     NOC_PATH_LEGACY_CONFIG
**Default Value**   etc/noc.yml
==================  ======================


.. _config-path-cythonize:

cythonize
~~~~~~~~~

==================  ==================
**YAML Path**       path.cythonize
**Key-Value Path**  path/cythonize
**Environment**     NOC_PATH_CYTHONIZE
**Default Value**   ./bin/cythonize
==================  ==================


.. _config-path-npkg_root:

npkg_root
~~~~~~~~~

==================  ====================
**YAML Path**       path.npkg_root
**Key-Value Path**  path/npkg_root
**Environment**     NOC_PATH_NPKG_ROOT
**Default Value**   /var/lib/noc/var/pkg
==================  ====================


.. _config-path-card_template_path:

card_template_path
~~~~~~~~~~~~~~~~~~

==================  ====================================
**YAML Path**       path.card_template_path
**Key-Value Path**  path/card_template_path
**Environment**     NOC_PATH_CARD_TEMPLATE_PATH
**Default Value**   services/card/templates/card.html.j2
==================  ====================================


.. _config-path-pm_templates:

pm_templates
~~~~~~~~~~~~

==================  =====================
**YAML Path**       path.pm_templates
**Key-Value Path**  path/pm_templates
**Environment**     NOC_PATH_PM_TEMPLATES
**Default Value**   templates/ddash/
==================  =====================


.. _config-pg:

pg
--


.. _config-pg-addresses:

addresses
~~~~~~~~~

==================  =============================================================================
**YAML Path**       pg.addresses
**Key-Value Path**  pg/addresses
**Environment**     NOC_PG_ADDRESSES
**Default Value**   ServiceParameter(service='postgres', wait=True, near=True, full_result=False)
==================  =============================================================================


.. _config-pg-db:

db
~~

==================  =========
**YAML Path**       pg.db
**Key-Value Path**  pg/db
**Environment**     NOC_PG_DB
**Default Value**   noc
==================  =========


.. _config-pg-user:

user
~~~~

==================  =================
**YAML Path**       pg.user
**Key-Value Path**  pg/user
**Environment**     NOC_PG_USER
**Default Value**   StringParameter()
==================  =================


.. _config-pg-password:

password
~~~~~~~~

==================  =================
**YAML Path**       pg.password
**Key-Value Path**  pg/password
**Environment**     NOC_PG_PASSWORD
**Default Value**   SecretParameter()
==================  =================


.. _config-pg-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ======================
**YAML Path**       pg.connect_timeout
**Key-Value Path**  pg/connect_timeout
**Environment**     NOC_PG_CONNECT_TIMEOUT
**Default Value**   5
==================  ======================


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
**Default Value**   IntParameter(min=0, max=255, default=0)
==================  =======================================


.. _config-ping-send_buffer:

send_buffer
~~~~~~~~~~~

==================  ====================
**YAML Path**       ping.send_buffer
**Key-Value Path**  ping/send_buffer
**Environment**     NOC_PING_SEND_BUFFER
**Default Value**   4 * 1048576
==================  ====================


.. _config-ping-receive_buffer:

receive_buffer
~~~~~~~~~~~~~~

==================  =======================
**YAML Path**       ping.receive_buffer
**Key-Value Path**  ping/receive_buffer
**Environment**     NOC_PING_RECEIVE_BUFFER
**Default Value**   4 * 1048576
==================  =======================


.. _config-pmwriter:

pmwriter
--------


.. _config-pmwriter-batch_size:

batch_size
~~~~~~~~~~

==================  =======================
**YAML Path**       pmwriter.batch_size
**Key-Value Path**  pmwriter/batch_size
**Environment**     NOC_PMWRITER_BATCH_SIZE
**Default Value**   2500
==================  =======================


.. _config-pmwriter-metrics_buffer:

metrics_buffer
~~~~~~~~~~~~~~

==================  ===========================
**YAML Path**       pmwriter.metrics_buffer
**Key-Value Path**  pmwriter/metrics_buffer
**Environment**     NOC_PMWRITER_METRICS_BUFFER
**Default Value**   50000
==================  ===========================


.. _config-pmwriter-read_from:

read_from
~~~~~~~~~

==================  ======================
**YAML Path**       pmwriter.read_from
**Key-Value Path**  pmwriter/read_from
**Environment**     NOC_PMWRITER_READ_FROM
**Default Value**   pmwriter
==================  ======================


.. _config-pmwriter-write_to:

write_to
~~~~~~~~

==================  =====================
**YAML Path**       pmwriter.write_to
**Key-Value Path**  pmwriter/write_to
**Environment**     NOC_PMWRITER_WRITE_TO
**Default Value**   influxdb
==================  =====================


.. _config-pmwriter-write_to_port:

write_to_port
~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       pmwriter.write_to_port
**Key-Value Path**  pmwriter/write_to_port
**Environment**     NOC_PMWRITER_WRITE_TO_PORT
**Default Value**   8086
==================  ==========================


.. _config-pmwriter-max_delay:

max_delay
~~~~~~~~~

==================  ======================
**YAML Path**       pmwriter.max_delay
**Key-Value Path**  pmwriter/max_delay
**Environment**     NOC_PMWRITER_MAX_DELAY
**Default Value**   1.0
==================  ======================


.. _config-proxy:

proxy
-----


.. _config-proxy-http_proxy:

http_proxy
~~~~~~~~~~

==================  ============================
**YAML Path**       proxy.http_proxy
**Key-Value Path**  proxy/http_proxy
**Environment**     NOC_PROXY_HTTP_PROXY
**Default Value**   os.environ.get('http_proxy')
==================  ============================


.. _config-proxy-https_proxy:

https_proxy
~~~~~~~~~~~

==================  =============================
**YAML Path**       proxy.https_proxy
**Key-Value Path**  proxy/https_proxy
**Environment**     NOC_PROXY_HTTPS_PROXY
**Default Value**   os.environ.get('https_proxy')
==================  =============================


.. _config-proxy-ftp_proxy:

ftp_proxy
~~~~~~~~~

==================  ===========================
**YAML Path**       proxy.ftp_proxy
**Key-Value Path**  proxy/ftp_proxy
**Environment**     NOC_PROXY_FTP_PROXY
**Default Value**   os.environ.get('ftp_proxy')
==================  ===========================


.. _config-rpc:

rpc
---


.. _config-rpc-retry_timeout:

retry_timeout
~~~~~~~~~~~~~

==================  =====================
**YAML Path**       rpc.retry_timeout
**Key-Value Path**  rpc/retry_timeout
**Environment**     NOC_RPC_RETRY_TIMEOUT
**Default Value**   0.1,0.5,1,3,10,30
==================  =====================


.. _config-rpc-sync_connect_timeout:

sync_connect_timeout
~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       rpc.sync_connect_timeout
**Key-Value Path**  rpc/sync_connect_timeout
**Environment**     NOC_RPC_SYNC_CONNECT_TIMEOUT
**Default Value**   20s
==================  ============================


.. _config-rpc-sync_request_timeout:

sync_request_timeout
~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       rpc.sync_request_timeout
**Key-Value Path**  rpc/sync_request_timeout
**Environment**     NOC_RPC_SYNC_REQUEST_TIMEOUT
**Default Value**   1h
==================  ============================


.. _config-rpc-sync_retry_timeout:

sync_retry_timeout
~~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       rpc.sync_retry_timeout
**Key-Value Path**  rpc/sync_retry_timeout
**Environment**     NOC_RPC_SYNC_RETRY_TIMEOUT
**Default Value**   1.0
==================  ==========================


.. _config-rpc-sync_retry_delta:

sync_retry_delta
~~~~~~~~~~~~~~~~

==================  ========================
**YAML Path**       rpc.sync_retry_delta
**Key-Value Path**  rpc/sync_retry_delta
**Environment**     NOC_RPC_SYNC_RETRY_DELTA
**Default Value**   2.0
==================  ========================


.. _config-rpc-sync_retries:

sync_retries
~~~~~~~~~~~~

==================  ====================
**YAML Path**       rpc.sync_retries
**Key-Value Path**  rpc/sync_retries
**Environment**     NOC_RPC_SYNC_RETRIES
**Default Value**   5
==================  ====================


.. _config-rpc-async_connect_timeout:

async_connect_timeout
~~~~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       rpc.async_connect_timeout
**Key-Value Path**  rpc/async_connect_timeout
**Environment**     NOC_RPC_ASYNC_CONNECT_TIMEOUT
**Default Value**   20s
==================  =============================


.. _config-rpc-async_request_timeout:

async_request_timeout
~~~~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       rpc.async_request_timeout
**Key-Value Path**  rpc/async_request_timeout
**Environment**     NOC_RPC_ASYNC_REQUEST_TIMEOUT
**Default Value**   1h
==================  =============================


.. _config-sae:

sae
---


.. _config-sae-db_threads:

db_threads
~~~~~~~~~~

==================  ==================
**YAML Path**       sae.db_threads
**Key-Value Path**  sae/db_threads
**Environment**     NOC_SAE_DB_THREADS
**Default Value**   20
==================  ==================


.. _config-sae-activator_resolution_retries:

activator_resolution_retries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

==================  ====================================
**YAML Path**       sae.activator_resolution_retries
**Key-Value Path**  sae/activator_resolution_retries
**Environment**     NOC_SAE_ACTIVATOR_RESOLUTION_RETRIES
**Default Value**   5
==================  ====================================


.. _config-sae-activator_resolution_timeout:

activator_resolution_timeout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

==================  ====================================
**YAML Path**       sae.activator_resolution_timeout
**Key-Value Path**  sae/activator_resolution_timeout
**Environment**     NOC_SAE_ACTIVATOR_RESOLUTION_TIMEOUT
**Default Value**   2s
==================  ====================================


.. _config-scheduler:

scheduler
---------


.. _config-scheduler-max_threads:

max_threads
~~~~~~~~~~~

==================  =========================
**YAML Path**       scheduler.max_threads
**Key-Value Path**  scheduler/max_threads
**Environment**     NOC_SCHEDULER_MAX_THREADS
**Default Value**   20
==================  =========================


.. _config-scheduler-submit_threshold_factor:

submit_threshold_factor
~~~~~~~~~~~~~~~~~~~~~~~

==================  =====================================
**YAML Path**       scheduler.submit_threshold_factor
**Key-Value Path**  scheduler/submit_threshold_factor
**Environment**     NOC_SCHEDULER_SUBMIT_THRESHOLD_FACTOR
**Default Value**   10
==================  =====================================


.. _config-scheduler-max_chunk_factor:

max_chunk_factor
~~~~~~~~~~~~~~~~

==================  ==============================
**YAML Path**       scheduler.max_chunk_factor
**Key-Value Path**  scheduler/max_chunk_factor
**Environment**     NOC_SCHEDULER_MAX_CHUNK_FACTOR
**Default Value**   1
==================  ==============================


.. _config-scheduler-updates_per_check:

updates_per_check
~~~~~~~~~~~~~~~~~

==================  ===============================
**YAML Path**       scheduler.updates_per_check
**Key-Value Path**  scheduler/updates_per_check
**Environment**     NOC_SCHEDULER_UPDATES_PER_CHECK
**Default Value**   4
==================  ===============================


.. _config-scheduler-cache_default_ttl:

cache_default_ttl
~~~~~~~~~~~~~~~~~

==================  ===============================
**YAML Path**       scheduler.cache_default_ttl
**Key-Value Path**  scheduler/cache_default_ttl
**Environment**     NOC_SCHEDULER_CACHE_DEFAULT_TTL
**Default Value**   1d
==================  ===============================


.. _config-scheduler-autointervaljob_interval:

autointervaljob_interval
~~~~~~~~~~~~~~~~~~~~~~~~

==================  ======================================
**YAML Path**       scheduler.autointervaljob_interval
**Key-Value Path**  scheduler/autointervaljob_interval
**Environment**     NOC_SCHEDULER_AUTOINTERVALJOB_INTERVAL
**Default Value**   1d
==================  ======================================


.. _config-scheduler-autointervaljob_initial_submit_interval:

autointervaljob_initial_submit_interval
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

==================  =====================================================
**YAML Path**       scheduler.autointervaljob_initial_submit_interval
**Key-Value Path**  scheduler/autointervaljob_initial_submit_interval
**Environment**     NOC_SCHEDULER_AUTOINTERVALJOB_INITIAL_SUBMIT_INTERVAL
**Default Value**   1d
==================  =====================================================


.. _config-script:

script
------


.. _config-script-timeout:

timeout
~~~~~~~

Default sa script script timeout

==================  ==================
**YAML Path**       script.timeout
**Key-Value Path**  script/timeout
**Environment**     NOC_SCRIPT_TIMEOUT
**Default Value**   2M
==================  ==================


.. _config-script-session_idle_timeout:

session_idle_timeout
~~~~~~~~~~~~~~~~~~~~

Default session timeout

==================  ===============================
**YAML Path**       script.session_idle_timeout
**Key-Value Path**  script/session_idle_timeout
**Environment**     NOC_SCRIPT_SESSION_IDLE_TIMEOUT
**Default Value**   1M
==================  ===============================


.. _config-script-caller_timeout:

caller_timeout
~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       script.caller_timeout
**Key-Value Path**  script/caller_timeout
**Environment**     NOC_SCRIPT_CALLER_TIMEOUT
**Default Value**   1M
==================  =========================


.. _config-script-calling_service:

calling_service
~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       script.calling_service
**Key-Value Path**  script/calling_service
**Environment**     NOC_SCRIPT_CALLING_SERVICE
**Default Value**   MTManager
==================  ==========================


.. _config-sentry:

sentry
------


.. _config-sentry-url:

url
~~~

==================  ==============
**YAML Path**       sentry.url
**Key-Value Path**  sentry/url
**Environment**     NOC_SENTRY_URL
**Default Value**
==================  ==============


.. _config-sync:

sync
----


.. _config-sync-config_ttl:

config_ttl
~~~~~~~~~~

==================  ===================
**YAML Path**       sync.config_ttl
**Key-Value Path**  sync/config_ttl
**Environment**     NOC_SYNC_CONFIG_TTL
**Default Value**   1d
==================  ===================


.. _config-sync-ttl_jitter:

ttl_jitter
~~~~~~~~~~

==================  ===================
**YAML Path**       sync.ttl_jitter
**Key-Value Path**  sync/ttl_jitter
**Environment**     NOC_SYNC_TTL_JITTER
**Default Value**   0.1
==================  ===================


.. _config-sync-expired_refresh_timeout:

expired_refresh_timeout
~~~~~~~~~~~~~~~~~~~~~~~

==================  ================================
**YAML Path**       sync.expired_refresh_timeout
**Key-Value Path**  sync/expired_refresh_timeout
**Environment**     NOC_SYNC_EXPIRED_REFRESH_TIMEOUT
**Default Value**   25
==================  ================================


.. _config-sync-expired_refresh_chunk:

expired_refresh_chunk
~~~~~~~~~~~~~~~~~~~~~

==================  ==============================
**YAML Path**       sync.expired_refresh_chunk
**Key-Value Path**  sync/expired_refresh_chunk
**Environment**     NOC_SYNC_EXPIRED_REFRESH_CHUNK
**Default Value**   100
==================  ==============================


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


.. _config-tgsender:

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


.. _config-threadpool:

threadpool
----------


.. _config-threadpool-idle_timeout:

idle_timeout
~~~~~~~~~~~~

==================  ===========================
**YAML Path**       threadpool.idle_timeout
**Key-Value Path**  threadpool/idle_timeout
**Environment**     NOC_THREADPOOL_IDLE_TIMEOUT
**Default Value**   30s
==================  ===========================


.. _config-threadpool-shutdown_timeout:

shutdown_timeout
~~~~~~~~~~~~~~~~

==================  ===============================
**YAML Path**       threadpool.shutdown_timeout
**Key-Value Path**  threadpool/shutdown_timeout
**Environment**     NOC_THREADPOOL_SHUTDOWN_TIMEOUT
**Default Value**   1M
==================  ===============================


.. _config-traceback:

traceback
---------


.. _config-traceback-reverse:

reverse
~~~~~~~

==================  =====================
**YAML Path**       traceback.reverse
**Key-Value Path**  traceback/reverse
**Environment**     NOC_TRACEBACK_REVERSE
**Default Value**   True
==================  =====================


.. _config-trapcollector:

trapcollector
-------------


.. _config-trapcollector-listen:

listen
~~~~~~

==================  ========================
**YAML Path**       trapcollector.listen
**Key-Value Path**  trapcollector/listen
**Environment**     NOC_TRAPCOLLECTOR_LISTEN
**Default Value**   0.0.0.0:162
==================  ========================


.. _config-web:

web
---


.. _config-web-api_row_limit:

api_row_limit
~~~~~~~~~~~~~

==================  =====================
**YAML Path**       web.api_row_limit
**Key-Value Path**  web/api_row_limit
**Environment**     NOC_WEB_API_ROW_LIMIT
**Default Value**   0
==================  =====================


.. _config-web-api_arch_alarm_limit:

api_arch_alarm_limit
~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML Path**       web.api_arch_alarm_limit
**Key-Value Path**  web/api_arch_alarm_limit
**Environment**     NOC_WEB_API_ARCH_ALARM_LIMIT
**Default Value**   4 * 86400
==================  ============================


.. _config-web-language:

language
~~~~~~~~

==================  ================
**YAML Path**       web.language
**Key-Value Path**  web/language
**Environment**     NOC_WEB_LANGUAGE
**Default Value**   en
==================  ================


.. _config-web-install_collection:

install_collection
~~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML Path**       web.install_collection
**Key-Value Path**  web/install_collection
**Environment**     NOC_WEB_INSTALL_COLLECTION
**Default Value**   False
==================  ==========================


.. _config-web-max_threads:

max_threads
~~~~~~~~~~~

==================  ===================
**YAML Path**       web.max_threads
**Key-Value Path**  web/max_threads
**Environment**     NOC_WEB_MAX_THREADS
**Default Value**   10
==================  ===================


.. _config-web-macdb_window:

macdb_window
~~~~~~~~~~~~

==================  ====================
**YAML Path**       web.macdb_window
**Key-Value Path**  web/macdb_window
**Environment**     NOC_WEB_MACDB_WINDOW
**Default Value**   4 * 86400
==================  ====================


.. _config-datasource:

datasource
----------


.. _config-datasource-chunk_size:

chunk_size
~~~~~~~~~~

==================  =========================
**YAML Path**       datasource.chunk_size
**Key-Value Path**  datasource/chunk_size
**Environment**     NOC_DATASOURCE_CHUNK_SIZE
**Default Value**   1000
==================  =========================


.. _config-datasource-max_threads:

max_threads
~~~~~~~~~~~

==================  ==========================
**YAML Path**       datasource.max_threads
**Key-Value Path**  datasource/max_threads
**Environment**     NOC_DATASOURCE_MAX_THREADS
**Default Value**   10
==================  ==========================


.. _config-datasource-default_ttl:

default_ttl
~~~~~~~~~~~

==================  ==========================
**YAML Path**       datasource.default_ttl
**Key-Value Path**  datasource/default_ttl
**Environment**     NOC_DATASOURCE_DEFAULT_TTL
**Default Value**   1h
==================  ==========================


.. _config-tests:

tests
-----


.. _config-tests-enable_coverage:

enable_coverage
~~~~~~~~~~~~~~~

==================  =========================
**YAML Path**       tests.enable_coverage
**Key-Value Path**  tests/enable_coverage
**Environment**     NOC_TESTS_ENABLE_COVERAGE
**Default Value**   False
==================  =========================


.. _config-tests-events_path:

events_path
~~~~~~~~~~~

==================  =======================
**YAML Path**       tests.events_path
**Key-Value Path**  tests/events_path
**Environment**     NOC_TESTS_EVENTS_PATH
**Default Value**   collections/test.events
==================  =======================


.. _config-tests-profilecheck_path:

profilecheck_path
~~~~~~~~~~~~~~~~~

==================  =============================
**YAML Path**       tests.profilecheck_path
**Key-Value Path**  tests/profilecheck_path
**Environment**     NOC_TESTS_PROFILECHECK_PATH
**Default Value**   collections/test.profilecheck
==================  =============================
