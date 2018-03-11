.. _admin-config:



Configuration Reference
=======================


.. contents:: On this page
    :local:
    :backlinks: none
    :depth: 1
    :class: singlecol


.. _config-Config:

Config
------


.. _config-Config-loglevel:

loglevel
~~~~~~~~

==================  ===================================================================================================================================================================
**YAML_Path**       Config.loglevel
**Key_Value_Path**  Config/loglevel
**Environment**     NOC_CONFIG_LOGLEVEL
**Default_Value**   MapParameter(default="info",
                    mappings={"critical": logging.CRITICAL,"error": logging.ERROR,"warning": logging.WARNING, "info": logging.INFO, "debug": logging.DEBUG}
==================  ===================================================================================================================================================================


Global
------

Global settings applicable to all services

.. _config-brand:

brand
~~~~~

==================  =========
**YAML_Path**       brand
**Key_Value_Path**  brand
**Environment**     NOC_BRAND
**Default_Value**   NOC
==================  =========


.. _config-global_n_instances:

global_n_instances
~~~~~~~~~~~~~~~~~~

==================  ======================
**YAML_Path**       global_n_instances
**Key_Value_Path**  global_n_instances
**Environment**     NOC_GLOBAL_N_INSTANCES
**Default_Value**   1
==================  ======================


.. _config-installation_name:

installation_name
~~~~~~~~~~~~~~~~~

==================  =========================
**YAML_Path**       installation_name
**Key_Value_Path**  installation_name
**Environment**     NOC_INSTALLATION_NAME
**Default_Value**   Unconfigured installation
==================  =========================


.. _config-instance:

instance
~~~~~~~~

==================  ============
**YAML_Path**       instance
**Key_Value_Path**  instance
**Environment**     NOC_INSTANCE
**Default_Value**   0
==================  ============


.. _config-language:

language
~~~~~~~~

==================  ============
**YAML_Path**       language
**Key_Value_Path**  language
**Environment**     NOC_LANGUAGE
**Default_Value**   en
==================  ============


.. _config-language_code:

language_code
~~~~~~~~~~~~~

==================  =================
**YAML_Path**       language_code
**Key_Value_Path**  language_code
**Environment**     NOC_LANGUAGE_CODE
**Default_Value**   en-us
==================  =================


.. _config-listen:

listen
~~~~~~

==================  ==========
**YAML_Path**       listen
**Key_Value_Path**  listen
**Environment**     NOC_LISTEN
**Default_Value**   auto:0
==================  ==========


.. _config-log_format:

log_format
~~~~~~~~~~

==================  ==================================
**YAML_Path**       log_format
**Key_Value_Path**  log_format
**Environment**     NOC_LOG_FORMAT
**Default_Value**   %(asctime)s [%(name)s] %(message)s
==================  ==================================


.. _config-thread_stack_size:

thread_stack_size
~~~~~~~~~~~~~~~~~

==================  =====================
**YAML_Path**       thread_stack_size
**Key_Value_Path**  thread_stack_size
**Environment**     NOC_THREAD_STACK_SIZE
**Default_Value**   0
==================  =====================


.. _config-node:

node
~~~~

==================  ====================
**YAML_Path**       node
**Key_Value_Path**  node
**Environment**     NOC_NODE
**Default_Value**   socket.gethostname()
==================  ====================


.. _config-pool:

pool
~~~~

==================  ==============================
**YAML_Path**       pool
**Key_Value_Path**  pool
**Environment**     NOC_POOL
**Default_Value**   os.environ.get("NOC_POOL", "")
==================  ==============================


.. _config-secret_key:

secret_key
~~~~~~~~~~

==================  ==============
**YAML_Path**       secret_key
**Key_Value_Path**  secret_key
**Environment**     NOC_SECRET_KEY
**Default_Value**   12345
==================  ==============


.. _config-timezone:

timezone
~~~~~~~~

==================  =============
**YAML_Path**       timezone
**Key_Value_Path**  timezone
**Environment**     NOC_TIMEZONE
**Default_Value**   Europe/Moscow
==================  =============


.. _config-activator:

activator
---------


.. _config-activator-tos:

tos
~~~

==================  =======================================
**YAML_Path**       activator.tos
**Key_Value_Path**  activator/tos
**Environment**     NOC_ACTIVATOR_TOS
**Default_Value**   IntParameter(min=0, max=255, default=0)
==================  =======================================


.. _config-activator-script_threads:

script_threads
~~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       activator.script_threads
**Key_Value_Path**  activator/script_threads
**Environment**     NOC_ACTIVATOR_SCRIPT_THREADS
**Default_Value**   10
==================  ============================


.. _config-activator-buffer_size:

buffer_size
~~~~~~~~~~~

==================  =========================
**YAML_Path**       activator.buffer_size
**Key_Value_Path**  activator/buffer_size
**Environment**     NOC_ACTIVATOR_BUFFER_SIZE
**Default_Value**   1048576
==================  =========================


.. _config-activator-connect_retries:

connect_retries
~~~~~~~~~~~~~~~

retries on immediate disconnect

==================  =============================
**YAML_Path**       activator.connect_retries
**Key_Value_Path**  activator/connect_retries
**Environment**     NOC_ACTIVATOR_CONNECT_RETRIES
**Default_Value**   3
==================  =============================


.. _config-activator-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

timeout after immediate disconnect

==================  =============================
**YAML_Path**       activator.connect_timeout
**Key_Value_Path**  activator/connect_timeout
**Environment**     NOC_ACTIVATOR_CONNECT_TIMEOUT
**Default_Value**   3
==================  =============================


.. _config-activator-http_connect_timeout:

http_connect_timeout
~~~~~~~~~~~~~~~~~~~~

==================  ==================================
**YAML_Path**       activator.http_connect_timeout
**Key_Value_Path**  activator/http_connect_timeout
**Environment**     NOC_ACTIVATOR_HTTP_CONNECT_TIMEOUT
**Default_Value**   20
==================  ==================================


.. _config-activator-http_request_timeout:

http_request_timeout
~~~~~~~~~~~~~~~~~~~~

==================  ==================================
**YAML_Path**       activator.http_request_timeout
**Key_Value_Path**  activator/http_request_timeout
**Environment**     NOC_ACTIVATOR_HTTP_REQUEST_TIMEOUT
**Default_Value**   30
==================  ==================================


.. _config-activator-http_validate_cert:

http_validate_cert
~~~~~~~~~~~~~~~~~~

==================  ================================
**YAML_Path**       activator.http_validate_cert
**Key_Value_Path**  activator/http_validate_cert
**Environment**     NOC_ACTIVATOR_HTTP_VALIDATE_CERT
**Default_Value**   False
==================  ================================


.. _config-audit:

audit
-----


.. _config-audit-command_ttl:

command_ttl
~~~~~~~~~~~

==================  =====================
**YAML_Path**       audit.command_ttl
**Key_Value_Path**  audit/command_ttl
**Environment**     NOC_AUDIT_COMMAND_TTL
**Default_Value**   1m
==================  =====================


.. _config-audit-login_ttl:

login_ttl
~~~~~~~~~

==================  ===================
**YAML_Path**       audit.login_ttl
**Key_Value_Path**  audit/login_ttl
**Environment**     NOC_AUDIT_LOGIN_TTL
**Default_Value**   1m
==================  ===================


.. _config-audit-reboot_ttl:

reboot_ttl
~~~~~~~~~~

==================  ====================
**YAML_Path**       audit.reboot_ttl
**Key_Value_Path**  audit/reboot_ttl
**Environment**     NOC_AUDIT_REBOOT_TTL
**Default_Value**   0
==================  ====================


.. _config-audit-config_ttl:

config_ttl
~~~~~~~~~~

==================  ====================
**YAML_Path**       audit.config_ttl
**Key_Value_Path**  audit/config_ttl
**Environment**     NOC_AUDIT_CONFIG_TTL
**Default_Value**   1y
==================  ====================


.. _config-audit-db_ttl:

db_ttl
~~~~~~

==================  ================
**YAML_Path**       audit.db_ttl
**Key_Value_Path**  audit/db_ttl
**Environment**     NOC_AUDIT_DB_TTL
**Default_Value**   5y
==================  ================


.. _config-audit-config_changed_ttl:

config_changed_ttl
~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       audit.config_changed_ttl
**Key_Value_Path**  audit/config_changed_ttl
**Environment**     NOC_AUDIT_CONFIG_CHANGED_TTL
**Default_Value**   1y
==================  ============================


.. _config-backup:

backup
------


.. _config-backup-keep_days:

keep_days
~~~~~~~~~

==================  ====================
**YAML_Path**       backup.keep_days
**Key_Value_Path**  backup/keep_days
**Environment**     NOC_BACKUP_KEEP_DAYS
**Default_Value**   14d
==================  ====================


.. _config-backup-keep_weeks:

keep_weeks
~~~~~~~~~~

==================  =====================
**YAML_Path**       backup.keep_weeks
**Key_Value_Path**  backup/keep_weeks
**Environment**     NOC_BACKUP_KEEP_WEEKS
**Default_Value**   12w
==================  =====================


.. _config-backup-keep_day_of_week:

keep_day_of_week
~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       backup.keep_day_of_week
**Key_Value_Path**  backup/keep_day_of_week
**Environment**     NOC_BACKUP_KEEP_DAY_OF_WEEK
**Default_Value**   6
==================  ===========================


.. _config-backup-keep_months:

keep_months
~~~~~~~~~~~

==================  ======================
**YAML_Path**       backup.keep_months
**Key_Value_Path**  backup/keep_months
**Environment**     NOC_BACKUP_KEEP_MONTHS
**Default_Value**   12
==================  ======================


.. _config-backup-keep_day_of_month:

keep_day_of_month
~~~~~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       backup.keep_day_of_month
**Key_Value_Path**  backup/keep_day_of_month
**Environment**     NOC_BACKUP_KEEP_DAY_OF_MONTH
**Default_Value**   1
==================  ============================


.. _config-bi:

bi
##


.. _config-bi-language:

language
~~~~~~~~

==================  ===============
**YAML_Path**       bi.language
**Key_Value_Path**  bi/language
**Environment**     NOC_BI_LANGUAGE
**Default_Value**   en
==================  ===============


.. _config-bi-query_threads:

query_threads
~~~~~~~~~~~~~

==================  ====================
**YAML_Path**       bi.query_threads
**Key_Value_Path**  bi/query_threads
**Environment**     NOC_BI_QUERY_THREADS
**Default_Value**   10
==================  ====================


.. _config-bi-extract_delay_alarms:

extract_delay_alarms
~~~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       bi.extract_delay_alarms
**Key_Value_Path**  bi/extract_delay_alarms
**Environment**     NOC_BI_EXTRACT_DELAY_ALARMS
**Default_Value**   1h
==================  ===========================


.. _config-bi-clean_delay_alarms:

clean_delay_alarms
~~~~~~~~~~~~~~~~~~

==================  =========================
**YAML_Path**       bi.clean_delay_alarms
**Key_Value_Path**  bi/clean_delay_alarms
**Environment**     NOC_BI_CLEAN_DELAY_ALARMS
**Default_Value**   1d
==================  =========================


.. _config-bi-reboot_interval:

reboot_interval
~~~~~~~~~~~~~~~

==================  ======================
**YAML_Path**       bi.reboot_interval
**Key_Value_Path**  bi/reboot_interval
**Environment**     NOC_BI_REBOOT_INTERVAL
**Default_Value**   1M
==================  ======================


.. _config-bi-extract_delay_reboots:

extract_delay_reboots
~~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       bi.extract_delay_reboots
**Key_Value_Path**  bi/extract_delay_reboots
**Environment**     NOC_BI_EXTRACT_DELAY_REBOOTS
**Default_Value**   1h
==================  ============================


.. _config-bi-clean_delay_reboots:

clean_delay_reboots
~~~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       bi.clean_delay_reboots
**Key_Value_Path**  bi/clean_delay_reboots
**Environment**     NOC_BI_CLEAN_DELAY_REBOOTS
**Default_Value**   1d
==================  ==========================


.. _config-bi-chunk_size:

chunk_size
~~~~~~~~~~

==================  =================
**YAML_Path**       bi.chunk_size
**Key_Value_Path**  bi/chunk_size
**Environment**     NOC_BI_CHUNK_SIZE
**Default_Value**   3000
==================  =================


.. _config-bi-extract_window:

extract_window
~~~~~~~~~~~~~~

==================  =====================
**YAML_Path**       bi.extract_window
**Key_Value_Path**  bi/extract_window
**Environment**     NOC_BI_EXTRACT_WINDOW
**Default_Value**   1d
==================  =====================


.. _config-bi-enable_alarms:

enable_alarms
~~~~~~~~~~~~~

==================  ====================
**YAML_Path**       bi.enable_alarms
**Key_Value_Path**  bi/enable_alarms
**Environment**     NOC_BI_ENABLE_ALARMS
**Default_Value**   False
==================  ====================


.. _config-bi-enable_reboots:

enable_reboots
~~~~~~~~~~~~~~

==================  =====================
**YAML_Path**       bi.enable_reboots
**Key_Value_Path**  bi/enable_reboots
**Environment**     NOC_BI_ENABLE_REBOOTS
**Default_Value**   False
==================  =====================


.. _config-bi-enable_managedobjects:

enable_managedobjects
~~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       bi.enable_managedobjects
**Key_Value_Path**  bi/enable_managedobjects
**Environment**     NOC_BI_ENABLE_MANAGEDOBJECTS
**Default_Value**   False
==================  ============================


.. _config-cache:

cache
-----


.. _config-cache-vcinterfacescount:

vcinterfacescount
~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       cache.vcinterfacescount
**Key_Value_Path**  cache/vcinterfacescount
**Environment**     NOC_CACHE_VCINTERFACESCOUNT
**Default_Value**   1h
==================  ===========================


.. _config-cache-vcprefixes:

vcprefixes
~~~~~~~~~~

==================  ====================
**YAML_Path**       cache.vcprefixes
**Key_Value_Path**  cache/vcprefixes
**Environment**     NOC_CACHE_VCPREFIXES
**Default_Value**   1h
==================  ====================


.. _config-cache-cache_class:

cache_class
~~~~~~~~~~~

==================  ===============================
**YAML_Path**       cache.cache_class
**Key_Value_Path**  cache/cache_class
**Environment**     NOC_CACHE_CACHE_CLASS
**Default_Value**   noc.core.cache.mongo.MongoCache
==================  ===============================


.. _config-cache-default_ttl:

default_ttl
~~~~~~~~~~~

==================  =====================
**YAML_Path**       cache.default_ttl
**Key_Value_Path**  cache/default_ttl
**Environment**     NOC_CACHE_DEFAULT_TTL
**Default_Value**   1d
==================  =====================


.. _config-cache-pool_size:

pool_size
~~~~~~~~~

==================  ===================
**YAML_Path**       cache.pool_size
**Key_Value_Path**  cache/pool_size
**Environment**     NOC_CACHE_POOL_SIZE
**Default_Value**   8
==================  ===================


.. _config-card:

card
----


.. _config-card-language:

language
~~~~~~~~

==================  =================
**YAML_Path**       card.language
**Key_Value_Path**  card/language
**Environment**     NOC_CARD_LANGUAGE
**Default_Value**   en
==================  =================


.. _config-card-alarmheat_tooltip_limit:

alarmheat_tooltip_limit
~~~~~~~~~~~~~~~~~~~~~~~

==================  ================================
**YAML_Path**       card.alarmheat_tooltip_limit
**Key_Value_Path**  card/alarmheat_tooltip_limit
**Environment**     NOC_CARD_ALARMHEAT_TOOLTIP_LIMIT
**Default_Value**   5
==================  ================================


.. _config-chwriter:

chwriter
--------


.. _config-chwriter-batch_size:

batch_size
~~~~~~~~~~

==================  =======================
**YAML_Path**       chwriter.batch_size
**Key_Value_Path**  chwriter/batch_size
**Environment**     NOC_CHWRITER_BATCH_SIZE
**Default_Value**   50000
==================  =======================


.. _config-chwriter-records_buffer:

records_buffer
~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       chwriter.records_buffer
**Key_Value_Path**  chwriter/records_buffer
**Environment**     NOC_CHWRITER_RECORDS_BUFFER
**Default_Value**   1000000
==================  ===========================


.. _config-chwriter-batch_delay_ms:

batch_delay_ms
~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       chwriter.batch_delay_ms
**Key_Value_Path**  chwriter/batch_delay_ms
**Environment**     NOC_CHWRITER_BATCH_DELAY_MS
**Default_Value**   10000
==================  ===========================


.. _config-chwriter-channel_expire_interval:

channel_expire_interval
~~~~~~~~~~~~~~~~~~~~~~~

==================  ====================================
**YAML_Path**       chwriter.channel_expire_interval
**Key_Value_Path**  chwriter/channel_expire_interval
**Environment**     NOC_CHWRITER_CHANNEL_EXPIRE_INTERVAL
**Default_Value**   5M
==================  ====================================


.. _config-chwriter-suspend_timeout_ms:

suspend_timeout_ms
~~~~~~~~~~~~~~~~~~

==================  ===============================
**YAML_Path**       chwriter.suspend_timeout_ms
**Key_Value_Path**  chwriter/suspend_timeout_ms
**Environment**     NOC_CHWRITER_SUSPEND_TIMEOUT_MS
**Default_Value**   3000
==================  ===============================


.. _config-chwriter-topic:

topic
~~~~~

==================  ==================
**YAML_Path**       chwriter.topic
**Key_Value_Path**  chwriter/topic
**Environment**     NOC_CHWRITER_TOPIC
**Default_Value**   chwriter
==================  ==================


.. _config-chwriter-write_to:

write_to
~~~~~~~~

==================  =====================
**YAML_Path**       chwriter.write_to
**Key_Value_Path**  chwriter/write_to
**Environment**     NOC_CHWRITER_WRITE_TO
**Default_Value**   StringParameter()
==================  =====================


.. _config-chwriter-max_in_flight:

max_in_flight
~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       chwriter.max_in_flight
**Key_Value_Path**  chwriter/max_in_flight
**Environment**     NOC_CHWRITER_MAX_IN_FLIGHT
**Default_Value**   10
==================  ==========================


.. _config-classifier:

classifier
----------


.. _config-classifier-lookup_handler:

lookup_handler
~~~~~~~~~~~~~~

==================  =============================================
**YAML_Path**       classifier.lookup_handler
**Key_Value_Path**  classifier/lookup_handler
**Environment**     NOC_CLASSIFIER_LOOKUP_HANDLER
**Default_Value**   noc.services.classifier.rulelookup.RuleLookup
==================  =============================================


.. _config-classifier-default_interface_profile:

default_interface_profile
~~~~~~~~~~~~~~~~~~~~~~~~~

==================  ========================================
**YAML_Path**       classifier.default_interface_profile
**Key_Value_Path**  classifier/default_interface_profile
**Environment**     NOC_CLASSIFIER_DEFAULT_INTERFACE_PROFILE
**Default_Value**   default
==================  ========================================


.. _config-classifier-default_rule:

default_rule
~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       classifier.default_rule
**Key_Value_Path**  classifier/default_rule
**Environment**     NOC_CLASSIFIER_DEFAULT_RULE
**Default_Value**   Unknown | Default
==================  ===========================


.. _config-clickhouse:

clickhouse
----------


.. _config-clickhouse-rw_addresses:

rw_addresses
~~~~~~~~~~~~

==================  =================================================
**YAML_Path**       clickhouse.rw_addresses
**Key_Value_Path**  clickhouse/rw_addresses
**Environment**     NOC_CLICKHOUSE_RW_ADDRESSES
**Default_Value**   ServiceParameter(service='clickhouse', wait=True)
==================  =================================================


.. _config-clickhouse-db:

db
--

==================  =================
**YAML_Path**       clickhouse.db
**Key_Value_Path**  clickhouse/db
**Environment**     NOC_CLICKHOUSE_DB
**Default_Value**   noc
==================  =================


.. _config-clickhouse-rw_user:

rw_user
~~~~~~~

==================  ======================
**YAML_Path**       clickhouse.rw_user
**Key_Value_Path**  clickhouse/rw_user
**Environment**     NOC_CLICKHOUSE_RW_USER
**Default_Value**   default
==================  ======================


.. _config-clickhouse-rw_password:

rw_password
~~~~~~~~~~~

==================  ==========================
**YAML_Path**       clickhouse.rw_password
**Key_Value_Path**  clickhouse/rw_password
**Environment**     NOC_CLICKHOUSE_RW_PASSWORD
**Default_Value**   SecretParameter()
==================  ==========================


.. _config-clickhouse-ro_addresses:

ro_addresses
~~~~~~~~~~~~

==================  =================================================
**YAML_Path**       clickhouse.ro_addresses
**Key_Value_Path**  clickhouse/ro_addresses
**Environment**     NOC_CLICKHOUSE_RO_ADDRESSES
**Default_Value**   ServiceParameter(service='clickhouse', wait=True)
==================  =================================================


.. _config-clickhouse-ro_user:

ro_user
~~~~~~~

==================  ======================
**YAML_Path**       clickhouse.ro_user
**Key_Value_Path**  clickhouse/ro_user
**Environment**     NOC_CLICKHOUSE_RO_USER
**Default_Value**   readonly
==================  ======================


.. _config-clickhouse-ro_password:

ro_password
~~~~~~~~~~~

==================  ==========================
**YAML_Path**       clickhouse.ro_password
**Key_Value_Path**  clickhouse/ro_password
**Environment**     NOC_CLICKHOUSE_RO_PASSWORD
**Default_Value**   SecretParameter()
==================  ==========================


.. _config-clickhouse-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ==============================
**YAML_Path**       clickhouse.request_timeout
**Key_Value_Path**  clickhouse/request_timeout
**Environment**     NOC_CLICKHOUSE_REQUEST_TIMEOUT
**Default_Value**   1h
==================  ==============================


.. _config-clickhouse-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ==============================
**YAML_Path**       clickhouse.connect_timeout
**Key_Value_Path**  clickhouse/connect_timeout
**Environment**     NOC_CLICKHOUSE_CONNECT_TIMEOUT
**Default_Value**   10s
==================  ==============================


.. _config-clickhouse-default_merge_tree_granularity:

default_merge_tree_granularity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

==================  =============================================
**YAML_Path**       clickhouse.default_merge_tree_granularity
**Key_Value_Path**  clickhouse/default_merge_tree_granularity
**Environment**     NOC_CLICKHOUSE_DEFAULT_MERGE_TREE_GRANULARITY
**Default_Value**   8192
==================  =============================================


.. _config-clickhouse-encoding:

encoding
~~~~~~~~

==================  ===================================
**YAML_Path**       clickhouse.encoding
**Key_Value_Path**  clickhouse/encoding
**Environment**     NOC_CLICKHOUSE_ENCODING
**Default_Value**   '', choices=['', 'deflate', 'gzip']
==================  ===================================


.. _config-clickhouse-cluster:

cluster
~~~~~~~

Cluster name for sharded/replicated configuration
Matches appropriative <remote_servers> part

==================  ======================
**YAML_Path**       clickhouse.cluster
**Key_Value_Path**  clickhouse/cluster
**Environment**     NOC_CLICKHOUSE_CLUSTER
**Default_Value**   StringParameter()
==================  ======================


.. _config-clickhouse-cluster_topology:

cluster_topology
~~~~~~~~~~~~~~~~

==================  ===============================
**YAML_Path**       clickhouse.cluster_topology
**Key_Value_Path**  clickhouse/cluster_topology
**Environment**     NOC_CLICKHOUSE_CLUSTER_TOPOLOGY
**Default_Value**   1
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
##


.. _config-cm-vcs_type:

vcs_type
~~~~~~~~

==================  ===========================================
**YAML_Path**       cm.vcs_type
**Key_Value_Path**  cm/vcs_type
**Environment**     NOC_CM_VCS_TYPE
**Default_Value**   'gridvcs', choices=['hg', 'CVS', 'gridvcs']
==================  ===========================================


.. _config-consul:

consul
------


.. _config-consul-token:

token
~~~~~

==================  =================
**YAML_Path**       consul.token
**Key_Value_Path**  consul/token
**Environment**     NOC_CONSUL_TOKEN
**Default_Value**   SecretParameter()
==================  =================


.. _config-consul-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       consul.connect_timeout
**Key_Value_Path**  consul/connect_timeout
**Environment**     NOC_CONSUL_CONNECT_TIMEOUT
**Default_Value**   5s
==================  ==========================


.. _config-consul-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       consul.request_timeout
**Key_Value_Path**  consul/request_timeout
**Environment**     NOC_CONSUL_REQUEST_TIMEOUT
**Default_Value**   1h
==================  ==========================


.. _config-consul-near_retry_timeout:

near_retry_timeout
~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       consul.near_retry_timeout
**Key_Value_Path**  consul/near_retry_timeout
**Environment**     NOC_CONSUL_NEAR_RETRY_TIMEOUT
**Default_Value**   1
==================  =============================


.. _config-consul-host:

host
~~~~

==================  ===============
**YAML_Path**       consul.host
**Key_Value_Path**  consul/host
**Environment**     NOC_CONSUL_HOST
**Default_Value**   consul
==================  ===============


.. _config-consul-port:

port
~~~~

==================  ===============
**YAML_Path**       consul.port
**Key_Value_Path**  consul/port
**Environment**     NOC_CONSUL_PORT
**Default_Value**   8500
==================  ===============


.. _config-consul-check_interval:

check_interval
~~~~~~~~~~~~~~

==================  =========================
**YAML_Path**       consul.check_interval
**Key_Value_Path**  consul/check_interval
**Environment**     NOC_CONSUL_CHECK_INTERVAL
**Default_Value**   10s
==================  =========================


.. _config-consul-check_timeout:

check_timeout
~~~~~~~~~~~~~

==================  ========================
**YAML_Path**       consul.check_timeout
**Key_Value_Path**  consul/check_timeout
**Environment**     NOC_CONSUL_CHECK_TIMEOUT
**Default_Value**   1s
==================  ========================


.. _config-consul-release:

release
~~~~~~~

==================  ==================
**YAML_Path**       consul.release
**Key_Value_Path**  consul/release
**Environment**     NOC_CONSUL_RELEASE
**Default_Value**   1M
==================  ==================


.. _config-consul-session_ttl:

session_ttl
~~~~~~~~~~~

==================  ======================
**YAML_Path**       consul.session_ttl
**Key_Value_Path**  consul/session_ttl
**Environment**     NOC_CONSUL_SESSION_TTL
**Default_Value**   10s
==================  ======================


.. _config-consul-lock_delay:

lock_delay
~~~~~~~~~~

==================  =====================
**YAML_Path**       consul.lock_delay
**Key_Value_Path**  consul/lock_delay
**Environment**     NOC_CONSUL_LOCK_DELAY
**Default_Value**   20s
==================  =====================


.. _config-consul-retry_timeout:

retry_timeout
~~~~~~~~~~~~~

==================  ========================
**YAML_Path**       consul.retry_timeout
**Key_Value_Path**  consul/retry_timeout
**Environment**     NOC_CONSUL_RETRY_TIMEOUT
**Default_Value**   1s
==================  ========================


.. _config-consul-keepalive_attempts:

keepalive_attempts
~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       consul.keepalive_attempts
**Key_Value_Path**  consul/keepalive_attempts
**Environment**     NOC_CONSUL_KEEPALIVE_ATTEMPTS
**Default_Value**   5
==================  =============================


.. _config-consul-base:

base
~~~~

kv lookup base

==================  ===============
**YAML_Path**       consul.base
**Key_Value_Path**  consul/base
**Environment**     NOC_CONSUL_BASE
**Default_Value**   noc
==================  ===============


.. _config-correlator:

correlator
----------


.. _config-correlator-max_threads:

max_threads
~~~~~~~~~~~

==================  ==========================
**YAML_Path**       correlator.max_threads
**Key_Value_Path**  correlator/max_threads
**Environment**     NOC_CORRELATOR_MAX_THREADS
**Default_Value**   20
==================  ==========================


.. _config-correlator-topology_rca_window:

topology_rca_window
~~~~~~~~~~~~~~~~~~~

==================  ==================================
**YAML_Path**       correlator.topology_rca_window
**Key_Value_Path**  correlator/topology_rca_window
**Environment**     NOC_CORRELATOR_TOPOLOGY_RCA_WINDOW
**Default_Value**   0
==================  ==================================


.. _config-correlator-oo_close_delay:

oo_close_delay
~~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       correlator.oo_close_delay
**Key_Value_Path**  correlator/oo_close_delay
**Environment**     NOC_CORRELATOR_OO_CLOSE_DELAY
**Default_Value**   20s
==================  =============================


.. _config-correlator-discovery_delay:

discovery_delay
~~~~~~~~~~~~~~~

==================  ==============================
**YAML_Path**       correlator.discovery_delay
**Key_Value_Path**  correlator/discovery_delay
**Environment**     NOC_CORRELATOR_DISCOVERY_DELAY
**Default_Value**   10M
==================  ==============================


.. _config-correlator-auto_escalation:

auto_escalation
~~~~~~~~~~~~~~~

==================  ==============================
**YAML_Path**       correlator.auto_escalation
**Key_Value_Path**  correlator/auto_escalation
**Environment**     NOC_CORRELATOR_AUTO_ESCALATION
**Default_Value**   True
==================  ==============================


.. _config-customization:

customization
-------------


.. _config-customization-favicon_url:

favicon_url
~~~~~~~~~~~

==================  =====================================
**YAML_Path**       customization.favicon_url
**Key_Value_Path**  customization/favicon_url
**Environment**     NOC_CUSTOMIZATION_FAVICON_URL
**Default_Value**   /static/img/logo_24x24_deep_azure.png
==================  =====================================


.. _config-customization-logo_url:

logo_url
~~~~~~~~

==================  ==========================
**YAML_Path**       customization.logo_url
**Key_Value_Path**  customization/logo_url
**Environment**     NOC_CUSTOMIZATION_LOGO_URL
**Default_Value**   /static/img/logo_white.svg
==================  ==========================


.. _config-customization-logo_width:

logo_width
~~~~~~~~~~

==================  ============================
**YAML_Path**       customization.logo_width
**Key_Value_Path**  customization/logo_width
**Environment**     NOC_CUSTOMIZATION_LOGO_WIDTH
**Default_Value**   24
==================  ============================


.. _config-customization-logo_height:

logo_height
~~~~~~~~~~~

==================  =============================
**YAML_Path**       customization.logo_height
**Key_Value_Path**  customization/logo_height
**Environment**     NOC_CUSTOMIZATION_LOGO_HEIGHT
**Default_Value**   24
==================  =============================


.. _config-customization-branding_color:

branding_color
~~~~~~~~~~~~~~

==================  ================================
**YAML_Path**       customization.branding_color
**Key_Value_Path**  customization/branding_color
**Environment**     NOC_CUSTOMIZATION_BRANDING_COLOR
**Default_Value**   #ffffff
==================  ================================


.. _config-customization-branding_background_color:

branding_background_color
~~~~~~~~~~~~~~~~~~~~~~~~~

==================  ===========================================
**YAML_Path**       customization.branding_background_color
**Key_Value_Path**  customization/branding_background_color
**Environment**     NOC_CUSTOMIZATION_BRANDING_BACKGROUND_COLOR
**Default_Value**   #34495e
==================  ===========================================


.. _config-customization-preview_theme:

preview_theme
~~~~~~~~~~~~~

==================  ===============================
**YAML_Path**       customization.preview_theme
**Key_Value_Path**  customization/preview_theme
**Environment**     NOC_CUSTOMIZATION_PREVIEW_THEME
**Default_Value**   midnight
==================  ===============================


.. _config-date_time_formats:

date_time_formats
-----------------


.. _config-date_time_formats-date_format:

date_format
~~~~~~~~~~~

==================  =================================
**YAML_Path**       date_time_formats.date_format
**Key_Value_Path**  date_time_formats/date_format
**Environment**     NOC_DATE_TIME_FORMATS_DATE_FORMAT
**Default_Value**   d.m.Y
==================  =================================


.. _config-date_time_formats-datetime_format:

datetime_format
~~~~~~~~~~~~~~~

==================  =====================================
**YAML_Path**       date_time_formats.datetime_format
**Key_Value_Path**  date_time_formats/datetime_format
**Environment**     NOC_DATE_TIME_FORMATS_DATETIME_FORMAT
**Default_Value**   d.m.Y H:i:s
==================  =====================================


.. _config-date_time_formats-month_day_format:

month_day_format
~~~~~~~~~~~~~~~~

==================  ======================================
**YAML_Path**       date_time_formats.month_day_format
**Key_Value_Path**  date_time_formats/month_day_format
**Environment**     NOC_DATE_TIME_FORMATS_MONTH_DAY_FORMAT
**Default_Value**   F j
==================  ======================================


.. _config-date_time_formats-time_format:

time_format
~~~~~~~~~~~

==================  =================================
**YAML_Path**       date_time_formats.time_format
**Key_Value_Path**  date_time_formats/time_format
**Environment**     NOC_DATE_TIME_FORMATS_TIME_FORMAT
**Default_Value**   H:i:s
==================  =================================


.. _config-date_time_formats-year_month_format:

year_month_format
~~~~~~~~~~~~~~~~~

==================  =======================================
**YAML_Path**       date_time_formats.year_month_format
**Key_Value_Path**  date_time_formats/year_month_format
**Environment**     NOC_DATE_TIME_FORMATS_YEAR_MONTH_FORMAT
**Default_Value**   F Y
==================  =======================================


.. _config-dcs:

dcs
---


.. _config-dcs-resolution_timeout:

resolution_timeout
~~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       dcs.resolution_timeout
**Key_Value_Path**  dcs/resolution_timeout
**Environment**     NOC_DCS_RESOLUTION_TIMEOUT
**Default_Value**   5M
==================  ==========================


.. _config-discovery:

discovery
---------


.. _config-discovery-max_threads:

max_threads
~~~~~~~~~~~

==================  =========================
**YAML_Path**       discovery.max_threads
**Key_Value_Path**  discovery/max_threads
**Environment**     NOC_DISCOVERY_MAX_THREADS
**Default_Value**   20
==================  =========================


.. _config-discovery-sample:

sample
~~~~~~

==================  ====================
**YAML_Path**       discovery.sample
**Key_Value_Path**  discovery/sample
**Environment**     NOC_DISCOVERY_SAMPLE
**Default_Value**   0
==================  ====================


.. _config-dns:

dns
---


.. _config-dns-warn_before_expired:

warn_before_expired
~~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       dns.warn_before_expired
**Key_Value_Path**  dns/warn_before_expired
**Environment**     NOC_DNS_WARN_BEFORE_EXPIRED
**Default_Value**   30d
==================  ===========================


.. _config-escalator:

escalator
---------


.. _config-escalator-max_threads:

max_threads
~~~~~~~~~~~

==================  =========================
**YAML_Path**       escalator.max_threads
**Key_Value_Path**  escalator/max_threads
**Environment**     NOC_ESCALATOR_MAX_THREADS
**Default_Value**   5
==================  =========================


.. _config-escalator-retry_timeout:

retry_timeout
~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       escalator.retry_timeout
**Key_Value_Path**  escalator/retry_timeout
**Environment**     NOC_ESCALATOR_RETRY_TIMEOUT
**Default_Value**   60s
==================  ===========================


.. _config-escalator-tt_escalation_limit:

tt_escalation_limit
~~~~~~~~~~~~~~~~~~~

==================  =================================
**YAML_Path**       escalator.tt_escalation_limit
**Key_Value_Path**  escalator/tt_escalation_limit
**Environment**     NOC_ESCALATOR_TT_ESCALATION_LIMIT
**Default_Value**   10
==================  =================================


.. _config-escalator-ets:

ets
~~~

==================  =================
**YAML_Path**       escalator.ets
**Key_Value_Path**  escalator/ets
**Environment**     NOC_ESCALATOR_ETS
**Default_Value**   60s
==================  =================


.. _config-escalator-wait_tt_check_interval:

wait_tt_check_interval
~~~~~~~~~~~~~~~~~~~~~~

==================  ====================================
**YAML_Path**       escalator.wait_tt_check_interval
**Key_Value_Path**  escalator/wait_tt_check_interval
**Environment**     NOC_ESCALATOR_WAIT_TT_CHECK_INTERVAL
**Default_Value**   60s
==================  ====================================


.. _config-escalator-sample:

sample
~~~~~~

==================  ====================
**YAML_Path**       escalator.sample
**Key_Value_Path**  escalator/sample
**Environment**     NOC_ESCALATOR_SAMPLE
**Default_Value**   0
==================  ====================


.. _config-features:

features
--------


.. _config-features-use_uvlib:

use_uvlib
~~~~~~~~~

==================  ======================
**YAML_Path**       features.use_uvlib
**Key_Value_Path**  features/use_uvlib
**Environment**     NOC_FEATURES_USE_UVLIB
**Default_Value**   False
==================  ======================


.. _config-features-cp:

cp
--

==================  ===============
**YAML_Path**       features.cp
**Key_Value_Path**  features/cp
**Environment**     NOC_FEATURES_CP
**Default_Value**   True
==================  ===============


.. _config-features-sentry:

sentry
~~~~~~

==================  ===================
**YAML_Path**       features.sentry
**Key_Value_Path**  features/sentry
**Environment**     NOC_FEATURES_SENTRY
**Default_Value**   False
==================  ===================


.. _config-features-traefik:

traefik
~~~~~~~

==================  ====================
**YAML_Path**       features.traefik
**Key_Value_Path**  features/traefik
**Environment**     NOC_FEATURES_TRAEFIK
**Default_Value**   False
==================  ====================


.. _config-features-cpclient:

cpclient
~~~~~~~~

==================  =====================
**YAML_Path**       features.cpclient
**Key_Value_Path**  features/cpclient
**Environment**     NOC_FEATURES_CPCLIENT
**Default_Value**   False
==================  =====================


.. _config-features-telemetry:

telemetry
~~~~~~~~~

Enable internal telemetry export to Clickhouse

==================  ======================
**YAML_Path**       features.telemetry
**Key_Value_Path**  features/telemetry
**Environment**     NOC_FEATURES_TELEMETRY
**Default_Value**   False
==================  ======================


.. _config-features-consul_healthchecks:

consul_healthchecks
~~~~~~~~~~~~~~~~~~~

While registering serive in consul also register health check

==================  ================================
**YAML_Path**       features.consul_healthchecks
**Key_Value_Path**  features/consul_healthchecks
**Environment**     NOC_FEATURES_CONSUL_HEALTHCHECKS
**Default_Value**   True
==================  ================================


.. _config-features-service_registration:

service_registration
~~~~~~~~~~~~~~~~~~~~

Permit consul self registration

==================  =================================
**YAML_Path**       features.service_registration
**Key_Value_Path**  features/service_registration
**Environment**     NOC_FEATURES_SERVICE_REGISTRATION
**Default_Value**   True
==================  =================================


.. _config-features-pypy:

pypy
~~~~

==================  =================
**YAML_Path**       features.pypy
**Key_Value_Path**  features/pypy
**Environment**     NOC_FEATURES_PYPY
**Default_Value**   False
==================  =================


.. _config-features-forensic:

forensic
~~~~~~~~

==================  =====================
**YAML_Path**       features.forensic
**Key_Value_Path**  features/forensic
**Environment**     NOC_FEATURES_FORENSIC
**Default_Value**   False
==================  =====================


.. _config-fm:

fm
--


.. _config-fm-active_window:

active_window
~~~~~~~~~~~~~

==================  ====================
**YAML_Path**       fm.active_window
**Key_Value_Path**  fm/active_window
**Environment**     NOC_FM_ACTIVE_WINDOW
**Default_Value**   1d
==================  ====================


.. _config-fm-keep_events_wo_alarm:

keep_events_wo_alarm
~~~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       fm.keep_events_wo_alarm
**Key_Value_Path**  fm/keep_events_wo_alarm
**Environment**     NOC_FM_KEEP_EVENTS_WO_ALARM
**Default_Value**   0
==================  ===========================


.. _config-fm-keep_events_with_alarm:

keep_events_with_alarm
~~~~~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       fm.keep_events_with_alarm
**Key_Value_Path**  fm/keep_events_with_alarm
**Environment**     NOC_FM_KEEP_EVENTS_WITH_ALARM
**Default_Value**   -1
==================  =============================


.. _config-fm-alarm_close_retries:

alarm_close_retries
~~~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       fm.alarm_close_retries
**Key_Value_Path**  fm/alarm_close_retries
**Environment**     NOC_FM_ALARM_CLOSE_RETRIES
**Default_Value**   5
==================  ==========================


.. _config-fm-outage_refresh:

outage_refresh
~~~~~~~~~~~~~~

==================  =====================
**YAML_Path**       fm.outage_refresh
**Key_Value_Path**  fm/outage_refresh
**Environment**     NOC_FM_OUTAGE_REFRESH
**Default_Value**   60s
==================  =====================


.. _config-fm-total_outage_refresh:

total_outage_refresh
~~~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       fm.total_outage_refresh
**Key_Value_Path**  fm/total_outage_refresh
**Environment**     NOC_FM_TOTAL_OUTAGE_REFRESH
**Default_Value**   60s
==================  ===========================


.. _config-geocoding:

geocoding
---------


.. _config-geocoding-order:

order
~~~~~

==================  ===================
**YAML_Path**       geocoding.order
**Key_Value_Path**  geocoding/order
**Environment**     NOC_GEOCODING_ORDER
**Default_Value**   yandex,google
==================  ===================


.. _config-geocoding-yandex_key:

yandex_key
~~~~~~~~~~

==================  ========================
**YAML_Path**       geocoding.yandex_key
**Key_Value_Path**  geocoding/yandex_key
**Environment**     NOC_GEOCODING_YANDEX_KEY
**Default_Value**
==================  ========================


.. _config-geocoding-google_key:

google_key
~~~~~~~~~~

==================  ========================
**YAML_Path**       geocoding.google_key
**Key_Value_Path**  geocoding/google_key
**Environment**     NOC_GEOCODING_GOOGLE_KEY
**Default_Value**
==================  ========================


.. _config-geocoding-google_language:

google_language
~~~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       geocoding.google_language
**Key_Value_Path**  geocoding/google_language
**Environment**     NOC_GEOCODING_GOOGLE_LANGUAGE
**Default_Value**   en
==================  =============================


.. _config-gis:

gis
---


.. _config-gis-ellipsoid:

ellipsoid
~~~~~~~~~

==================  =================
**YAML_Path**       gis.ellipsoid
**Key_Value_Path**  gis/ellipsoid
**Environment**     NOC_GIS_ELLIPSOID
**Default_Value**   PZ-90
==================  =================


.. _config-gis-enable_osm:

enable_osm
~~~~~~~~~~

==================  ==================
**YAML_Path**       gis.enable_osm
**Key_Value_Path**  gis/enable_osm
**Environment**     NOC_GIS_ENABLE_OSM
**Default_Value**   True
==================  ==================


.. _config-gis-enable_google_sat:

enable_google_sat
~~~~~~~~~~~~~~~~~

==================  =========================
**YAML_Path**       gis.enable_google_sat
**Key_Value_Path**  gis/enable_google_sat
**Environment**     NOC_GIS_ENABLE_GOOGLE_SAT
**Default_Value**   False
==================  =========================


.. _config-gis-enable_google_roadmap:

enable_google_roadmap
~~~~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       gis.enable_google_roadmap
**Key_Value_Path**  gis/enable_google_roadmap
**Environment**     NOC_GIS_ENABLE_GOOGLE_ROADMAP
**Default_Value**   False
==================  =============================


.. _config-gis-tile_size:

tile_size
~~~~~~~~~

Tile size 256x256

==================  =================
**YAML_Path**       gis.tile_size
**Key_Value_Path**  gis/tile_size
**Environment**     NOC_GIS_TILE_SIZE
**Default_Value**   256
==================  =================


.. _config-gis-tilecache_padding:

tilecache_padding
~~~~~~~~~~~~~~~~~

==================  =========================
**YAML_Path**       gis.tilecache_padding
**Key_Value_Path**  gis/tilecache_padding
**Environment**     NOC_GIS_TILECACHE_PADDING
**Default_Value**   0
==================  =========================


.. _config-grafanads:

grafanads
---------


.. _config-grafanads-db_threads:

db_threads
~~~~~~~~~~

==================  ========================
**YAML_Path**       grafanads.db_threads
**Key_Value_Path**  grafanads/db_threads
**Environment**     NOC_GRAFANADS_DB_THREADS
**Default_Value**   10
==================  ========================


.. _config-http_client:

http_client
-----------


.. _config-http_client-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ===============================
**YAML_Path**       http_client.connect_timeout
**Key_Value_Path**  http_client/connect_timeout
**Environment**     NOC_HTTP_CLIENT_CONNECT_TIMEOUT
**Default_Value**   10s
==================  ===============================


.. _config-http_client-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ===============================
**YAML_Path**       http_client.request_timeout
**Key_Value_Path**  http_client/request_timeout
**Environment**     NOC_HTTP_CLIENT_REQUEST_TIMEOUT
**Default_Value**   1h
==================  ===============================


.. _config-http_client-user_agent:

user_agent
~~~~~~~~~~

==================  ==========================
**YAML_Path**       http_client.user_agent
**Key_Value_Path**  http_client/user_agent
**Environment**     NOC_HTTP_CLIENT_USER_AGENT
**Default_Value**   noc
==================  ==========================


.. _config-http_client-buffer_size:

buffer_size
~~~~~~~~~~~

==================  ===========================
**YAML_Path**       http_client.buffer_size
**Key_Value_Path**  http_client/buffer_size
**Environment**     NOC_HTTP_CLIENT_BUFFER_SIZE
**Default_Value**   128 * 1024
==================  ===========================


.. _config-http_client-max_redirects:

max_redirects
~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       http_client.max_redirects
**Key_Value_Path**  http_client/max_redirects
**Environment**     NOC_HTTP_CLIENT_MAX_REDIRECTS
**Default_Value**   5
==================  =============================


.. _config-http_client-ns_cache_size:

ns_cache_size
~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       http_client.ns_cache_size
**Key_Value_Path**  http_client/ns_cache_size
**Environment**     NOC_HTTP_CLIENT_NS_CACHE_SIZE
**Default_Value**   1000
==================  =============================


.. _config-http_client-resolver_ttl:

resolver_ttl
~~~~~~~~~~~~

==================  ============================
**YAML_Path**       http_client.resolver_ttl
**Key_Value_Path**  http_client/resolver_ttl
**Environment**     NOC_HTTP_CLIENT_RESOLVER_TTL
**Default_Value**   3s
==================  ============================


.. _config-http_client-http_port:

http_port
~~~~~~~~~

==================  =========================
**YAML_Path**       http_client.http_port
**Key_Value_Path**  http_client/http_port
**Environment**     NOC_HTTP_CLIENT_HTTP_PORT
**Default_Value**   80
==================  =========================


.. _config-http_client-https_port:

https_port
~~~~~~~~~~

==================  ==========================
**YAML_Path**       http_client.https_port
**Key_Value_Path**  http_client/https_port
**Environment**     NOC_HTTP_CLIENT_HTTPS_PORT
**Default_Value**   443
==================  ==========================


.. _config-http_client-validate_certs:

validate_certs
~~~~~~~~~~~~~~

Have to be set as True

==================  ==============================
**YAML_Path**       http_client.validate_certs
**Key_Value_Path**  http_client/validate_certs
**Environment**     NOC_HTTP_CLIENT_VALIDATE_CERTS
**Default_Value**   False
==================  ==============================


.. _config-influxdb:

influxdb
--------


.. _config-influxdb-addresses:

addresses
~~~~~~~~~

==================  ===============================================
**YAML_Path**       influxdb.addresses
**Key_Value_Path**  influxdb/addresses
**Environment**     NOC_INFLUXDB_ADDRESSES
**Default_Value**   ServiceParameter(service='influxdb', wait=True)
==================  ===============================================


.. _config-influxdb-db:

db
~~

==================  ===============
**YAML_Path**       influxdb.db
**Key_Value_Path**  influxdb/db
**Environment**     NOC_INFLUXDB_DB
**Default_Value**   noc
==================  ===============


.. _config-influxdb-user:

user
~~~~

==================  =================
**YAML_Path**       influxdb.user
**Key_Value_Path**  influxdb/user
**Environment**     NOC_INFLUXDB_USER
**Default_Value**   StringParameter()
==================  =================


.. _config-influxdb-password:

password
~~~~~~~~

==================  =====================
**YAML_Path**       influxdb.password
**Key_Value_Path**  influxdb/password
**Environment**     NOC_INFLUXDB_PASSWORD
**Default_Value**   SecretParameter()
==================  =====================


.. _config-influxdb-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       influxdb.request_timeout
**Key_Value_Path**  influxdb/request_timeout
**Environment**     NOC_INFLUXDB_REQUEST_TIMEOUT
**Default_Value**   10M
==================  ============================


.. _config-influxdb-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       influxdb.connect_timeout
**Key_Value_Path**  influxdb/connect_timeout
**Environment**     NOC_INFLUXDB_CONNECT_TIMEOUT
**Default_Value**   10s
==================  ============================


.. _config-logging:

logging
-------


.. _config-logging-log_api_calls:

log_api_calls
~~~~~~~~~~~~~

==================  =========================
**YAML_Path**       logging.log_api_calls
**Key_Value_Path**  logging/log_api_calls
**Environment**     NOC_LOGGING_LOG_API_CALLS
**Default_Value**   False
==================  =========================


.. _config-logging-log_sql_statements:

log_sql_statements
~~~~~~~~~~~~~~~~~~

==================  ==============================
**YAML_Path**       logging.log_sql_statements
**Key_Value_Path**  logging/log_sql_statements
**Environment**     NOC_LOGGING_LOG_SQL_STATEMENTS
**Default_Value**   False
==================  ==============================


.. _config-login:

login
-----


.. _config-login-methods:

methods
~~~~~~~

==================  =================
**YAML_Path**       login.methods
**Key_Value_Path**  login/methods
**Environment**     NOC_LOGIN_METHODS
**Default_Value**   local
==================  =================


.. _config-login-session_ttl:

session_ttl
~~~~~~~~~~~

==================  =====================
**YAML_Path**       login.session_ttl
**Key_Value_Path**  login/session_ttl
**Environment**     NOC_LOGIN_SESSION_TTL
**Default_Value**   7d
==================  =====================


.. _config-login-language:

language
~~~~~~~~

==================  ==================
**YAML_Path**       login.language
**Key_Value_Path**  login/language
**Environment**     NOC_LOGIN_LANGUAGE
**Default_Value**   en
==================  ==================


.. _config-login-restrict_to_group:

restrict_to_group
~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       login.restrict_to_group
**Key_Value_Path**  login/restrict_to_group
**Environment**     NOC_LOGIN_RESTRICT_TO_GROUP
**Default_Value**
==================  ===========================


.. _config-login-single_session_group:

single_session_group
~~~~~~~~~~~~~~~~~~~~

==================  ==============================
**YAML_Path**       login.single_session_group
**Key_Value_Path**  login/single_session_group
**Environment**     NOC_LOGIN_SINGLE_SESSION_GROUP
**Default_Value**
==================  ==============================


.. _config-login-mutual_exclusive_group:

mutual_exclusive_group
~~~~~~~~~~~~~~~~~~~~~~

==================  ================================
**YAML_Path**       login.mutual_exclusive_group
**Key_Value_Path**  login/mutual_exclusive_group
**Environment**     NOC_LOGIN_MUTUAL_EXCLUSIVE_GROUP
**Default_Value**
==================  ================================


.. _config-login-idle_timeout:

idle_timeout
~~~~~~~~~~~~

==================  ======================
**YAML_Path**       login.idle_timeout
**Key_Value_Path**  login/idle_timeout
**Environment**     NOC_LOGIN_IDLE_TIMEOUT
**Default_Value**   1w
==================  ======================


.. _config-login-pam_service:

pam_service
~~~~~~~~~~~

==================  =====================
**YAML_Path**       login.pam_service
**Key_Value_Path**  login/pam_service
**Environment**     NOC_LOGIN_PAM_SERVICE
**Default_Value**   noc
==================  =====================


.. _config-login-radius_secret:

radius_secret
~~~~~~~~~~~~~

==================  =======================
**YAML_Path**       login.radius_secret
**Key_Value_Path**  login/radius_secret
**Environment**     NOC_LOGIN_RADIUS_SECRET
**Default_Value**   noc
==================  =======================


.. _config-login-radius_server:

radius_server
~~~~~~~~~~~~~

==================  =======================
**YAML_Path**       login.radius_server
**Key_Value_Path**  login/radius_server
**Environment**     NOC_LOGIN_RADIUS_SERVER
**Default_Value**   StringParameter()
==================  =======================


.. _config-login-user_cookie_ttl:

user_cookie_ttl
~~~~~~~~~~~~~~~

==================  =========================
**YAML_Path**       login.user_cookie_ttl
**Key_Value_Path**  login/user_cookie_ttl
**Environment**     NOC_LOGIN_USER_COOKIE_TTL
**Default_Value**   1
==================  =========================


.. _config-mailsender:

mailsender
----------


.. _config-mailsender-smtp_server:

smtp_server
~~~~~~~~~~~

==================  ==========================
**YAML_Path**       mailsender.smtp_server
**Key_Value_Path**  mailsender/smtp_server
**Environment**     NOC_MAILSENDER_SMTP_SERVER
**Default_Value**   StringParameter()
==================  ==========================


.. _config-mailsender-smtp_port:

smtp_port
~~~~~~~~~

==================  ========================
**YAML_Path**       mailsender.smtp_port
**Key_Value_Path**  mailsender/smtp_port
**Environment**     NOC_MAILSENDER_SMTP_PORT
**Default_Value**   25
==================  ========================


.. _config-mailsender-use_tls:

use_tls
~~~~~~~

==================  ======================
**YAML_Path**       mailsender.use_tls
**Key_Value_Path**  mailsender/use_tls
**Environment**     NOC_MAILSENDER_USE_TLS
**Default_Value**   False
==================  ======================


.. _config-mailsender-helo_hostname:

helo_hostname
~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       mailsender.helo_hostname
**Key_Value_Path**  mailsender/helo_hostname
**Environment**     NOC_MAILSENDER_HELO_HOSTNAME
**Default_Value**   noc
==================  ============================


.. _config-mailsender-from_address:

from_address
~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       mailsender.from_address
**Key_Value_Path**  mailsender/from_address
**Environment**     NOC_MAILSENDER_FROM_ADDRESS
**Default_Value**   noc@example.com
==================  ===========================


.. _config-mailsender-smtp_user:

smtp_user
~~~~~~~~~

==================  ========================
**YAML_Path**       mailsender.smtp_user
**Key_Value_Path**  mailsender/smtp_user
**Environment**     NOC_MAILSENDER_SMTP_USER
**Default_Value**   StringParameter()
==================  ========================


.. _config-mailsender-smtp_password:

smtp_password
~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       mailsender.smtp_password
**Key_Value_Path**  mailsender/smtp_password
**Environment**     NOC_MAILSENDER_SMTP_PASSWORD
**Default_Value**   SecretParameter()
==================  ============================


.. _config-memcached:

memcached
---------


.. _config-memcached-addresses:

addresses
~~~~~~~~~

==================  ==================================================================
**YAML_Path**       memcached.addresses
**Key_Value_Path**  memcached/addresses
**Environment**     NOC_MEMCACHED_ADDRESSES
**Default_Value**   ServiceParameter(service='memcached', wait=True, full_result=True)
==================  ==================================================================


.. _config-memcached-pool_size:

pool_size
~~~~~~~~~

==================  =======================
**YAML_Path**       memcached.pool_size
**Key_Value_Path**  memcached/pool_size
**Environment**     NOC_MEMCACHED_POOL_SIZE
**Default_Value**   8
==================  =======================


.. _config-memcached-default_ttl:

default_ttl
~~~~~~~~~~~

==================  =========================
**YAML_Path**       memcached.default_ttl
**Key_Value_Path**  memcached/default_ttl
**Environment**     NOC_MEMCACHED_DEFAULT_TTL
**Default_Value**   1d
==================  =========================


.. _config-mongo:

mongo
-----


.. _config-mongo-addresses:

addresses
~~~~~~~~~

==================  ============================================
**YAML_Path**       mongo.addresses
**Key_Value_Path**  mongo/addresses
**Environment**     NOC_MONGO_ADDRESSES
**Default_Value**   ServiceParameter(service='mongo', wait=True)
==================  ============================================


.. _config-mongo-db:

db
~~

==================  ============
**YAML_Path**       mongo.db
**Key_Value_Path**  mongo/db
**Environment**     NOC_MONGO_DB
**Default_Value**   noc
==================  ============


.. _config-mongo-user:

user
~~~~

==================  =================
**YAML_Path**       mongo.user
**Key_Value_Path**  mongo/user
**Environment**     NOC_MONGO_USER
**Default_Value**   StringParameter()
==================  =================


.. _config-mongo-password:

password
~~~~~~~~

==================  ==================
**YAML_Path**       mongo.password
**Key_Value_Path**  mongo/password
**Environment**     NOC_MONGO_PASSWORD
**Default_Value**   SecretParameter()
==================  ==================


.. _config-mongo-rs:

rs
~~

==================  =================
**YAML_Path**       mongo.rs
**Key_Value_Path**  mongo/rs
**Environment**     NOC_MONGO_RS
**Default_Value**   StringParameter()
==================  =================


.. _config-mongo-retries:

retries
~~~~~~~

==================  =================
**YAML_Path**       mongo.retries
**Key_Value_Path**  mongo/retries
**Environment**     NOC_MONGO_RETRIES
**Default_Value**   20
==================  =================


.. _config-mongo-timeout:

timeout
~~~~~~~

==================  =================
**YAML_Path**       mongo.timeout
**Key_Value_Path**  mongo/timeout
**Environment**     NOC_MONGO_TIMEOUT
**Default_Value**   3s
==================  =================


.. _config-mrt:

mrt
---


.. _config-mrt-max_concurrency:

max_concurrency
~~~~~~~~~~~~~~~

==================  =======================
**YAML_Path**       mrt.max_concurrency
**Key_Value_Path**  mrt/max_concurrency
**Environment**     NOC_MRT_MAX_CONCURRENCY
**Default_Value**   50
==================  =======================


.. _config-nsqd:

nsqd
----


.. _config-nsqd-addresses:

addresses
~~~~~~~~~

==================  =========================================================================
**YAML_Path**       nsqd.addresses
**Key_Value_Path**  nsqd/addresses
**Environment**     NOC_NSQD_ADDRESSES
**Default_Value**   ServiceParameter(service='nsqd', wait=True, near=True, full_result=False)
==================  =========================================================================


.. _config-nsqd-http_addresses:

http_addresses
~~~~~~~~~~~~~~

==================  =============================================================================
**YAML_Path**       nsqd.http_addresses
**Key_Value_Path**  nsqd/http_addresses
**Environment**     NOC_NSQD_HTTP_ADDRESSES
**Default_Value**   ServiceParameter(service='nsqdhttp', wait=True, near=True, full_result=False)
==================  =============================================================================


.. _config-nsqd-pub_retry_delay:

pub_retry_delay
~~~~~~~~~~~~~~~

==================  ========================
**YAML_Path**       nsqd.pub_retry_delay
**Key_Value_Path**  nsqd/pub_retry_delay
**Environment**     NOC_NSQD_PUB_RETRY_DELAY
**Default_Value**   0.1
==================  ========================


.. _config-nsqd-ch_chunk_size:

ch_chunk_size
~~~~~~~~~~~~~

==================  ======================
**YAML_Path**       nsqd.ch_chunk_size
**Key_Value_Path**  nsqd/ch_chunk_size
**Environment**     NOC_NSQD_CH_CHUNK_SIZE
**Default_Value**   4000
==================  ======================


.. _config-nsqd-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ========================
**YAML_Path**       nsqd.connect_timeout
**Key_Value_Path**  nsqd/connect_timeout
**Environment**     NOC_NSQD_CONNECT_TIMEOUT
**Default_Value**   3s
==================  ========================


.. _config-nsqd-request_timeout:

request_timeout
~~~~~~~~~~~~~~~

==================  ========================
**YAML_Path**       nsqd.request_timeout
**Key_Value_Path**  nsqd/request_timeout
**Environment**     NOC_NSQD_REQUEST_TIMEOUT
**Default_Value**   30s
==================  ========================


.. _config-nsqd-reconnect_interval:

reconnect_interval
~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       nsqd.reconnect_interval
**Key_Value_Path**  nsqd/reconnect_interval
**Environment**     NOC_NSQD_RECONNECT_INTERVAL
**Default_Value**   15
==================  ===========================


.. _config-nsqd-compression:

compression
~~~~~~~~~~~

==================  =====================================
**YAML_Path**       nsqd.compression
**Key_Value_Path**  nsqd/compression
**Environment**     NOC_NSQD_COMPRESSION
**Default_Value**   '', choices=['', 'deflate', 'snappy']
==================  =====================================


.. _config-nsqd-compression_level:

compression_level
~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       nsqd.compression_level
**Key_Value_Path**  nsqd/compression_level
**Environment**     NOC_NSQD_COMPRESSION_LEVEL
**Default_Value**   6
==================  ==========================


.. _config-nsqd-max_in_flight:

max_in_flight
~~~~~~~~~~~~~

==================  ======================
**YAML_Path**       nsqd.max_in_flight
**Key_Value_Path**  nsqd/max_in_flight
**Environment**     NOC_NSQD_MAX_IN_FLIGHT
**Default_Value**   1
==================  ======================


.. _config-nsqlookupd:

nsqlookupd
----------


.. _config-nsqlookupd-addresses:

addresses
~~~~~~~~~

==================  ===============================================================================
**YAML_Path**       nsqlookupd.addresses
**Key_Value_Path**  nsqlookupd/addresses
**Environment**     NOC_NSQLOOKUPD_ADDRESSES
**Default_Value**   ServiceParameter(service='nsqlookupd', wait=True, near=True, full_result=False)
==================  ===============================================================================


.. _config-nsqlookupd-http_addresses:

http_addresses
~~~~~~~~~~~~~~

==================  ========================================================================
**YAML_Path**       nsqlookupd.http_addresses
**Key_Value_Path**  nsqlookupd/http_addresses
**Environment**     NOC_NSQLOOKUPD_HTTP_ADDRESSES
**Default_Value**   ServiceParameter(service='nsqlookupdhttp', wait=True, full_result=False)
==================  ========================================================================


.. _config-path:

path
----


.. _config-path-smilint:

smilint
~~~~~~~

==================  =================
**YAML_Path**       path.smilint
**Key_Value_Path**  path/smilint
**Environment**     NOC_PATH_SMILINT
**Default_Value**   StringParameter()
==================  =================


.. _config-path-smidump:

smidump
~~~~~~~

==================  =================
**YAML_Path**       path.smidump
**Key_Value_Path**  path/smidump
**Environment**     NOC_PATH_SMIDUMP
**Default_Value**   StringParameter()
==================  =================


.. _config-path-dig:

dig
~~~

==================  =================
**YAML_Path**       path.dig
**Key_Value_Path**  path/dig
**Environment**     NOC_PATH_DIG
**Default_Value**   StringParameter()
==================  =================


.. _config-path-vcs_path:

vcs_path
~~~~~~~~

==================  =================
**YAML_Path**       path.vcs_path
**Key_Value_Path**  path/vcs_path
**Environment**     NOC_PATH_VCS_PATH
**Default_Value**   /usr/local/bin/hg
==================  =================


.. _config-path-repo:

repo
~~~~

==================  =============
**YAML_Path**       path.repo
**Key_Value_Path**  path/repo
**Environment**     NOC_PATH_REPO
**Default_Value**   /var/repo
==================  =============


.. _config-path-config_mirror_path:

config_mirror_path
~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       path.config_mirror_path
**Key_Value_Path**  path/config_mirror_path
**Environment**     NOC_PATH_CONFIG_MIRROR_PATH
**Default_Value**   StringParameter('')
==================  ===========================


.. _config-path-backup_dir:

backup_dir
~~~~~~~~~~

==================  ===================
**YAML_Path**       path.backup_dir
**Key_Value_Path**  path/backup_dir
**Environment**     NOC_PATH_BACKUP_DIR
**Default_Value**   /var/backup
==================  ===================


.. _config-path-etl_import:

etl_import
~~~~~~~~~~

==================  ===================
**YAML_Path**       path.etl_import
**Key_Value_Path**  path/etl_import
**Environment**     NOC_PATH_ETL_IMPORT
**Default_Value**   /var/lib/noc/import
==================  ===================


.. _config-path-ssh_key_prefix:

ssh_key_prefix
~~~~~~~~~~~~~~

==================  =======================
**YAML_Path**       path.ssh_key_prefix
**Key_Value_Path**  path/ssh_key_prefix
**Environment**     NOC_PATH_SSH_KEY_PREFIX
**Default_Value**   etc/noc_ssh
==================  =======================


.. _config-path-beef_prefix:

beef_prefix
~~~~~~~~~~~

==================  ====================
**YAML_Path**       path.beef_prefix
**Key_Value_Path**  path/beef_prefix
**Environment**     NOC_PATH_BEEF_PREFIX
**Default_Value**   /var/lib/noc/beef/sa
==================  ====================


.. _config-path-cp_new:

cp_new
~~~~~~

==================  =============================
**YAML_Path**       path.cp_new
**Key_Value_Path**  path/cp_new
**Environment**     NOC_PATH_CP_NEW
**Default_Value**   /var/lib/noc/cp/crashinfo/new
==================  =============================


.. _config-path-bi_data_prefix:

bi_data_prefix
~~~~~~~~~~~~~~

==================  =======================
**YAML_Path**       path.bi_data_prefix
**Key_Value_Path**  path/bi_data_prefix
**Environment**     NOC_PATH_BI_DATA_PREFIX
**Default_Value**   /var/lib/noc/bi
==================  =======================


.. _config-path-babel_cfg:

babel_cfg
~~~~~~~~~

==================  ==================
**YAML_Path**       path.babel_cfg
**Key_Value_Path**  path/babel_cfg
**Environment**     NOC_PATH_BABEL_CFG
**Default_Value**   etc/babel.cfg
==================  ==================


.. _config-path-babel:

babel
~~~~~

==================  ==============
**YAML_Path**       path.babel
**Key_Value_Path**  path/babel
**Environment**     NOC_PATH_BABEL
**Default_Value**   ./bin/pybabel
==================  ==============


.. _config-path-pojson:

pojson
~~~~~~

==================  ===============
**YAML_Path**       path.pojson
**Key_Value_Path**  path/pojson
**Environment**     NOC_PATH_POJSON
**Default_Value**   ./bin/pojson
==================  ===============


.. _config-path-collection_fm_mibs:

collection_fm_mibs
~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       path.collection_fm_mibs
**Key_Value_Path**  path/collection_fm_mibs
**Environment**     NOC_PATH_COLLECTION_FM_MIBS
**Default_Value**   collections/fm.mibs/
==================  ===========================


.. _config-path-supervisor_cfg:

supervisor_cfg
~~~~~~~~~~~~~~

==================  =======================
**YAML_Path**       path.supervisor_cfg
**Key_Value_Path**  path/supervisor_cfg
**Environment**     NOC_PATH_SUPERVISOR_CFG
**Default_Value**   etc/noc_services.conf
==================  =======================


.. _config-path-legacy_config:

legacy_config
~~~~~~~~~~~~~

==================  ======================
**YAML_Path**       path.legacy_config
**Key_Value_Path**  path/legacy_config
**Environment**     NOC_PATH_LEGACY_CONFIG
**Default_Value**   etc/noc.yml
==================  ======================


.. _config-path-cythonize:

cythonize
~~~~~~~~~

==================  ==================
**YAML_Path**       path.cythonize
**Key_Value_Path**  path/cythonize
**Environment**     NOC_PATH_CYTHONIZE
**Default_Value**   ./bin/cythonize
==================  ==================


.. _config-path-npkg_root:

npkg_root
~~~~~~~~~

==================  ====================
**YAML_Path**       path.npkg_root
**Key_Value_Path**  path/npkg_root
**Environment**     NOC_PATH_NPKG_ROOT
**Default_Value**   /var/lib/noc/var/pkg
==================  ====================


.. _config-path-card_template_path:

card_template_path
~~~~~~~~~~~~~~~~~~

==================  ====================================
**YAML_Path**       path.card_template_path
**Key_Value_Path**  path/card_template_path
**Environment**     NOC_PATH_CARD_TEMPLATE_PATH
**Default_Value**   services/card/templates/card.html.j2
==================  ====================================


.. _config-path-pm_templates:

pm_templates
~~~~~~~~~~~~

==================  =====================
**YAML_Path**       path.pm_templates
**Key_Value_Path**  path/pm_templates
**Environment**     NOC_PATH_PM_TEMPLATES
**Default_Value**   templates/ddash/
==================  =====================


.. _config-pg:

pg
--


.. _config-pg-addresses:

addresses
~~~~~~~~~

==================  =============================================================================
**YAML_Path**       pg.addresses
**Key_Value_Path**  pg/addresses
**Environment**     NOC_PG_ADDRESSES
**Default_Value**   ServiceParameter(service='postgres', wait=True, near=True, full_result=False)
==================  =============================================================================


.. _config-pg-db:

db
~~

==================  =========
**YAML_Path**       pg.db
**Key_Value_Path**  pg/db
**Environment**     NOC_PG_DB
**Default_Value**   noc
==================  =========


.. _config-pg-user:

user
~~~~

==================  =================
**YAML_Path**       pg.user
**Key_Value_Path**  pg/user
**Environment**     NOC_PG_USER
**Default_Value**   StringParameter()
==================  =================


.. _config-pg-password:

password
~~~~~~~~

==================  =================
**YAML_Path**       pg.password
**Key_Value_Path**  pg/password
**Environment**     NOC_PG_PASSWORD
**Default_Value**   SecretParameter()
==================  =================


.. _config-pg-connect_timeout:

connect_timeout
~~~~~~~~~~~~~~~

==================  ======================
**YAML_Path**       pg.connect_timeout
**Key_Value_Path**  pg/connect_timeout
**Environment**     NOC_PG_CONNECT_TIMEOUT
**Default_Value**   5
==================  ======================


.. _config-ping:

ping
----


.. _config-ping-throttle_threshold:

throttle_threshold
~~~~~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       ping.throttle_threshold
**Key_Value_Path**  ping/throttle_threshold
**Environment**     NOC_PING_THROTTLE_THRESHOLD
**Default_Value**   FloatParameter()
==================  ===========================


.. _config-ping-restore_threshold:

restore_threshold
~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       ping.restore_threshold
**Key_Value_Path**  ping/restore_threshold
**Environment**     NOC_PING_RESTORE_THRESHOLD
**Default_Value**   FloatParameter()
==================  ==========================


.. _config-ping-tos:

tos
~~~

==================  =======================================
**YAML_Path**       ping.tos
**Key_Value_Path**  ping/tos
**Environment**     NOC_PING_TOS
**Default_Value**   IntParameter(min=0, max=255, default=0)
==================  =======================================


.. _config-ping-send_buffer:

send_buffer
~~~~~~~~~~~

==================  ====================
**YAML_Path**       ping.send_buffer
**Key_Value_Path**  ping/send_buffer
**Environment**     NOC_PING_SEND_BUFFER
**Default_Value**   4 * 1048576
==================  ====================


.. _config-ping-receive_buffer:

receive_buffer
~~~~~~~~~~~~~~

==================  =======================
**YAML_Path**       ping.receive_buffer
**Key_Value_Path**  ping/receive_buffer
**Environment**     NOC_PING_RECEIVE_BUFFER
**Default_Value**   4 * 1048576
==================  =======================


.. _config-pmwriter:

pmwriter
--------


.. _config-pmwriter-batch_size:

batch_size
~~~~~~~~~~

==================  =======================
**YAML_Path**       pmwriter.batch_size
**Key_Value_Path**  pmwriter/batch_size
**Environment**     NOC_PMWRITER_BATCH_SIZE
**Default_Value**   2500
==================  =======================


.. _config-pmwriter-metrics_buffer:

metrics_buffer
~~~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       pmwriter.metrics_buffer
**Key_Value_Path**  pmwriter/metrics_buffer
**Environment**     NOC_PMWRITER_METRICS_BUFFER
**Default_Value**   50000
==================  ===========================


.. _config-pmwriter-read_from:

read_from
~~~~~~~~~

==================  ======================
**YAML_Path**       pmwriter.read_from
**Key_Value_Path**  pmwriter/read_from
**Environment**     NOC_PMWRITER_READ_FROM
**Default_Value**   pmwriter
==================  ======================


.. _config-pmwriter-write_to:

write_to
~~~~~~~~

==================  =====================
**YAML_Path**       pmwriter.write_to
**Key_Value_Path**  pmwriter/write_to
**Environment**     NOC_PMWRITER_WRITE_TO
**Default_Value**   influxdb
==================  =====================


.. _config-pmwriter-write_to_port:

write_to_port
~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       pmwriter.write_to_port
**Key_Value_Path**  pmwriter/write_to_port
**Environment**     NOC_PMWRITER_WRITE_TO_PORT
**Default_Value**   8086
==================  ==========================


.. _config-pmwriter-max_delay:

max_delay
~~~~~~~~~

==================  ======================
**YAML_Path**       pmwriter.max_delay
**Key_Value_Path**  pmwriter/max_delay
**Environment**     NOC_PMWRITER_MAX_DELAY
**Default_Value**   1.0
==================  ======================


.. _config-proxy:

proxy
-----


.. _config-proxy-http_proxy:

http_proxy
~~~~~~~~~~

==================  ============================
**YAML_Path**       proxy.http_proxy
**Key_Value_Path**  proxy/http_proxy
**Environment**     NOC_PROXY_HTTP_PROXY
**Default_Value**   os.environ.get('http_proxy')
==================  ============================


.. _config-proxy-https_proxy:

https_proxy
~~~~~~~~~~~

==================  =============================
**YAML_Path**       proxy.https_proxy
**Key_Value_Path**  proxy/https_proxy
**Environment**     NOC_PROXY_HTTPS_PROXY
**Default_Value**   os.environ.get('https_proxy')
==================  =============================


.. _config-proxy-ftp_proxy:

ftp_proxy
~~~~~~~~~

==================  ===========================
**YAML_Path**       proxy.ftp_proxy
**Key_Value_Path**  proxy/ftp_proxy
**Environment**     NOC_PROXY_FTP_PROXY
**Default_Value**   os.environ.get('ftp_proxy')
==================  ===========================


.. _config-rpc:

rpc
---


.. _config-rpc-retry_timeout:

retry_timeout
~~~~~~~~~~~~~

==================  =====================
**YAML_Path**       rpc.retry_timeout
**Key_Value_Path**  rpc/retry_timeout
**Environment**     NOC_RPC_RETRY_TIMEOUT
**Default_Value**   0.1,0.5,1,3,10,30
==================  =====================


.. _config-rpc-sync_connect_timeout:

sync_connect_timeout
~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       rpc.sync_connect_timeout
**Key_Value_Path**  rpc/sync_connect_timeout
**Environment**     NOC_RPC_SYNC_CONNECT_TIMEOUT
**Default_Value**   20s
==================  ============================


.. _config-rpc-sync_request_timeout:

sync_request_timeout
~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       rpc.sync_request_timeout
**Key_Value_Path**  rpc/sync_request_timeout
**Environment**     NOC_RPC_SYNC_REQUEST_TIMEOUT
**Default_Value**   1h
==================  ============================


.. _config-rpc-sync_retry_timeout:

sync_retry_timeout
~~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       rpc.sync_retry_timeout
**Key_Value_Path**  rpc/sync_retry_timeout
**Environment**     NOC_RPC_SYNC_RETRY_TIMEOUT
**Default_Value**   1.0
==================  ==========================


.. _config-rpc-sync_retry_delta:

sync_retry_delta
~~~~~~~~~~~~~~~~

==================  ========================
**YAML_Path**       rpc.sync_retry_delta
**Key_Value_Path**  rpc/sync_retry_delta
**Environment**     NOC_RPC_SYNC_RETRY_DELTA
**Default_Value**   2.0
==================  ========================


.. _config-rpc-sync_retries:

sync_retries
~~~~~~~~~~~~

==================  ====================
**YAML_Path**       rpc.sync_retries
**Key_Value_Path**  rpc/sync_retries
**Environment**     NOC_RPC_SYNC_RETRIES
**Default_Value**   5
==================  ====================


.. _config-rpc-async_connect_timeout:

async_connect_timeout
~~~~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       rpc.async_connect_timeout
**Key_Value_Path**  rpc/async_connect_timeout
**Environment**     NOC_RPC_ASYNC_CONNECT_TIMEOUT
**Default_Value**   20s
==================  =============================


.. _config-rpc-async_request_timeout:

async_request_timeout
~~~~~~~~~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       rpc.async_request_timeout
**Key_Value_Path**  rpc/async_request_timeout
**Environment**     NOC_RPC_ASYNC_REQUEST_TIMEOUT
**Default_Value**   1h
==================  =============================


.. _config-sae:

sae
---


.. _config-sae-db_threads:

db_threads
~~~~~~~~~~

==================  ==================
**YAML_Path**       sae.db_threads
**Key_Value_Path**  sae/db_threads
**Environment**     NOC_SAE_DB_THREADS
**Default_Value**   20
==================  ==================


.. _config-sae-activator_resolution_retries:

activator_resolution_retries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

==================  ====================================
**YAML_Path**       sae.activator_resolution_retries
**Key_Value_Path**  sae/activator_resolution_retries
**Environment**     NOC_SAE_ACTIVATOR_RESOLUTION_RETRIES
**Default_Value**   5
==================  ====================================


.. _config-sae-activator_resolution_timeout:

activator_resolution_timeout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

==================  ====================================
**YAML_Path**       sae.activator_resolution_timeout
**Key_Value_Path**  sae/activator_resolution_timeout
**Environment**     NOC_SAE_ACTIVATOR_RESOLUTION_TIMEOUT
**Default_Value**   2s
==================  ====================================


.. _config-scheduler:

scheduler
---------


.. _config-scheduler-max_threads:

max_threads
~~~~~~~~~~~

==================  =========================
**YAML_Path**       scheduler.max_threads
**Key_Value_Path**  scheduler/max_threads
**Environment**     NOC_SCHEDULER_MAX_THREADS
**Default_Value**   20
==================  =========================


.. _config-scheduler-submit_threshold_factor:

submit_threshold_factor
~~~~~~~~~~~~~~~~~~~~~~~

==================  =====================================
**YAML_Path**       scheduler.submit_threshold_factor
**Key_Value_Path**  scheduler/submit_threshold_factor
**Environment**     NOC_SCHEDULER_SUBMIT_THRESHOLD_FACTOR
**Default_Value**   10
==================  =====================================


.. _config-scheduler-max_chunk_factor:

max_chunk_factor
~~~~~~~~~~~~~~~~

==================  ==============================
**YAML_Path**       scheduler.max_chunk_factor
**Key_Value_Path**  scheduler/max_chunk_factor
**Environment**     NOC_SCHEDULER_MAX_CHUNK_FACTOR
**Default_Value**   1
==================  ==============================


.. _config-scheduler-updates_per_check:

updates_per_check
~~~~~~~~~~~~~~~~~

==================  ===============================
**YAML_Path**       scheduler.updates_per_check
**Key_Value_Path**  scheduler/updates_per_check
**Environment**     NOC_SCHEDULER_UPDATES_PER_CHECK
**Default_Value**   4
==================  ===============================


.. _config-scheduler-cache_default_ttl:

cache_default_ttl
~~~~~~~~~~~~~~~~~

==================  ===============================
**YAML_Path**       scheduler.cache_default_ttl
**Key_Value_Path**  scheduler/cache_default_ttl
**Environment**     NOC_SCHEDULER_CACHE_DEFAULT_TTL
**Default_Value**   1d
==================  ===============================


.. _config-scheduler-autointervaljob_interval:

autointervaljob_interval
~~~~~~~~~~~~~~~~~~~~~~~~

==================  ======================================
**YAML_Path**       scheduler.autointervaljob_interval
**Key_Value_Path**  scheduler/autointervaljob_interval
**Environment**     NOC_SCHEDULER_AUTOINTERVALJOB_INTERVAL
**Default_Value**   1d
==================  ======================================


.. _config-scheduler-autointervaljob_initial_submit_interval:

autointervaljob_initial_submit_interval
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

==================  =====================================================
**YAML_Path**       scheduler.autointervaljob_initial_submit_interval
**Key_Value_Path**  scheduler/autointervaljob_initial_submit_interval
**Environment**     NOC_SCHEDULER_AUTOINTERVALJOB_INITIAL_SUBMIT_INTERVAL
**Default_Value**   1d
==================  =====================================================


.. _config-script:

script
------


.. _config-script-timeout:

timeout
~~~~~~~

Default sa script script timeout

==================  ==================
**YAML_Path**       script.timeout
**Key_Value_Path**  script/timeout
**Environment**     NOC_SCRIPT_TIMEOUT
**Default_Value**   2M
==================  ==================


.. _config-script-session_idle_timeout:

session_idle_timeout
~~~~~~~~~~~~~~~~~~~~

Default session timeout

==================  ===============================
**YAML_Path**       script.session_idle_timeout
**Key_Value_Path**  script/session_idle_timeout
**Environment**     NOC_SCRIPT_SESSION_IDLE_TIMEOUT
**Default_Value**   1M
==================  ===============================


.. _config-script-caller_timeout:

caller_timeout
~~~~~~~~~~~~~~

==================  =========================
**YAML_Path**       script.caller_timeout
**Key_Value_Path**  script/caller_timeout
**Environment**     NOC_SCRIPT_CALLER_TIMEOUT
**Default_Value**   1M
==================  =========================


.. _config-script-calling_service:

calling_service
~~~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       script.calling_service
**Key_Value_Path**  script/calling_service
**Environment**     NOC_SCRIPT_CALLING_SERVICE
**Default_Value**   MTManager
==================  ==========================


.. _config-sentry:

sentry
------


.. _config-sentry-url:

url
~~~

==================  ==============
**YAML_Path**       sentry.url
**Key_Value_Path**  sentry/url
**Environment**     NOC_SENTRY_URL
**Default_Value**
==================  ==============


.. _config-sync:

sync
----


.. _config-sync-config_ttl:

config_ttl
~~~~~~~~~~

==================  ===================
**YAML_Path**       sync.config_ttl
**Key_Value_Path**  sync/config_ttl
**Environment**     NOC_SYNC_CONFIG_TTL
**Default_Value**   1d
==================  ===================


.. _config-sync-ttl_jitter:

ttl_jitter
~~~~~~~~~~

==================  ===================
**YAML_Path**       sync.ttl_jitter
**Key_Value_Path**  sync/ttl_jitter
**Environment**     NOC_SYNC_TTL_JITTER
**Default_Value**   0.1
==================  ===================


.. _config-sync-expired_refresh_timeout:

expired_refresh_timeout
~~~~~~~~~~~~~~~~~~~~~~~

==================  ================================
**YAML_Path**       sync.expired_refresh_timeout
**Key_Value_Path**  sync/expired_refresh_timeout
**Environment**     NOC_SYNC_EXPIRED_REFRESH_TIMEOUT
**Default_Value**   25
==================  ================================


.. _config-sync-expired_refresh_chunk:

expired_refresh_chunk
~~~~~~~~~~~~~~~~~~~~~

==================  ==============================
**YAML_Path**       sync.expired_refresh_chunk
**Key_Value_Path**  sync/expired_refresh_chunk
**Environment**     NOC_SYNC_EXPIRED_REFRESH_CHUNK
**Default_Value**   100
==================  ==============================


.. _config-syslogcollector:

syslogcollector
---------------


.. _config-syslogcollector-listen:

listen
~~~~~~

==================  ==========================
**YAML_Path**       syslogcollector.listen
**Key_Value_Path**  syslogcollector/listen
**Environment**     NOC_SYSLOGCOLLECTOR_LISTEN
**Default_Value**   0.0.0.0:514
==================  ==========================


.. _config-tgsender:

tgsender
--------


.. _config-tgsender-token:

token
~~~~~

==================  ==================
**YAML_Path**       tgsender.token
**Key_Value_Path**  tgsender/token
**Environment**     NOC_TGSENDER_TOKEN
**Default_Value**   SecretParameter()
==================  ==================


.. _config-tgsender-retry_timeout:

retry_timeout
~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       tgsender.retry_timeout
**Key_Value_Path**  tgsender/retry_timeout
**Environment**     NOC_TGSENDER_RETRY_TIMEOUT
**Default_Value**   2
==================  ==========================


.. _config-tgsender-use_proxy:

use_proxy
~~~~~~~~~

==================  ======================
**YAML_Path**       tgsender.use_proxy
**Key_Value_Path**  tgsender/use_proxy
**Environment**     NOC_TGSENDER_USE_PROXY
**Default_Value**   False
==================  ======================


.. _config-threadpool:

threadpool
----------


.. _config-threadpool-idle_timeout:

idle_timeout
~~~~~~~~~~~~

==================  ===========================
**YAML_Path**       threadpool.idle_timeout
**Key_Value_Path**  threadpool/idle_timeout
**Environment**     NOC_THREADPOOL_IDLE_TIMEOUT
**Default_Value**   30s
==================  ===========================


.. _config-threadpool-shutdown_timeout:

shutdown_timeout
~~~~~~~~~~~~~~~~

==================  ===============================
**YAML_Path**       threadpool.shutdown_timeout
**Key_Value_Path**  threadpool/shutdown_timeout
**Environment**     NOC_THREADPOOL_SHUTDOWN_TIMEOUT
**Default_Value**   1M
==================  ===============================


.. _config-traceback:

traceback
---------


.. _config-traceback-reverse:

reverse
~~~~~~~

==================  =====================
**YAML_Path**       traceback.reverse
**Key_Value_Path**  traceback/reverse
**Environment**     NOC_TRACEBACK_REVERSE
**Default_Value**   True
==================  =====================


.. _config-trapcollector:

trapcollector
-------------


.. _config-trapcollector-listen:

listen
~~~~~~

==================  ========================
**YAML_Path**       trapcollector.listen
**Key_Value_Path**  trapcollector/listen
**Environment**     NOC_TRAPCOLLECTOR_LISTEN
**Default_Value**   0.0.0.0:162
==================  ========================


.. _config-web:

web
---


.. _config-web-api_row_limit:

api_row_limit
~~~~~~~~~~~~~

==================  =====================
**YAML_Path**       web.api_row_limit
**Key_Value_Path**  web/api_row_limit
**Environment**     NOC_WEB_API_ROW_LIMIT
**Default_Value**   0
==================  =====================


.. _config-web-api_arch_alarm_limit:

api_arch_alarm_limit
~~~~~~~~~~~~~~~~~~~~

==================  ============================
**YAML_Path**       web.api_arch_alarm_limit
**Key_Value_Path**  web/api_arch_alarm_limit
**Environment**     NOC_WEB_API_ARCH_ALARM_LIMIT
**Default_Value**   4 * 86400
==================  ============================


.. _config-web-language:

language
~~~~~~~~

==================  ================
**YAML_Path**       web.language
**Key_Value_Path**  web/language
**Environment**     NOC_WEB_LANGUAGE
**Default_Value**   en
==================  ================


.. _config-web-install_collection:

install_collection
~~~~~~~~~~~~~~~~~~

==================  ==========================
**YAML_Path**       web.install_collection
**Key_Value_Path**  web/install_collection
**Environment**     NOC_WEB_INSTALL_COLLECTION
**Default_Value**   False
==================  ==========================


.. _config-web-max_threads:

max_threads
~~~~~~~~~~~

==================  ===================
**YAML_Path**       web.max_threads
**Key_Value_Path**  web/max_threads
**Environment**     NOC_WEB_MAX_THREADS
**Default_Value**   10
==================  ===================


.. _config-web-macdb_window:

macdb_window
~~~~~~~~~~~~

==================  ====================
**YAML_Path**       web.macdb_window
**Key_Value_Path**  web/macdb_window
**Environment**     NOC_WEB_MACDB_WINDOW
**Default_Value**   4 * 86400
==================  ====================


.. _config-datasource:

datasource
----------


.. _config-datasource-chunk_size:

chunk_size
~~~~~~~~~~

==================  =========================
**YAML_Path**       datasource.chunk_size
**Key_Value_Path**  datasource/chunk_size
**Environment**     NOC_DATASOURCE_CHUNK_SIZE
**Default_Value**   1000
==================  =========================


.. _config-datasource-max_threads:

max_threads
~~~~~~~~~~~

==================  ==========================
**YAML_Path**       datasource.max_threads
**Key_Value_Path**  datasource/max_threads
**Environment**     NOC_DATASOURCE_MAX_THREADS
**Default_Value**   10
==================  ==========================


.. _config-datasource-default_ttl:

default_ttl
~~~~~~~~~~~

==================  ==========================
**YAML_Path**       datasource.default_ttl
**Key_Value_Path**  datasource/default_ttl
**Environment**     NOC_DATASOURCE_DEFAULT_TTL
**Default_Value**   1h
==================  ==========================


.. _config-tests:

tests
-----


.. _config-tests-enable_coverage:

enable_coverage
~~~~~~~~~~~~~~~

==================  =========================
**YAML_Path**       tests.enable_coverage
**Key_Value_Path**  tests/enable_coverage
**Environment**     NOC_TESTS_ENABLE_COVERAGE
**Default_Value**   False
==================  =========================


.. _config-tests-events_path:

events_path
~~~~~~~~~~~

==================  =======================
**YAML_Path**       tests.events_path
**Key_Value_Path**  tests/events_path
**Environment**     NOC_TESTS_EVENTS_PATH
**Default_Value**   collections/test.events
==================  =======================


.. _config-tests-profilecheck_path:

profilecheck_path
~~~~~~~~~~~~~~~~~

==================  =============================
**YAML_Path**       tests.profilecheck_path
**Key_Value_Path**  tests/profilecheck_path
**Environment**     NOC_TESTS_PROFILECHECK_PATH
**Default_Value**   collections/test.profilecheck
==================  =============================
