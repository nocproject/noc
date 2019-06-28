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


