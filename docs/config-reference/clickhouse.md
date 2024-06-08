# [clickhouse] section

Clickhouse service configuration

## rw_addresses

|                |                                   |
| -------------- | --------------------------------- |
| Default value  | `service="clickhouse", wait=True` |
| YAML Path      | `clickhouse.rw_addresses`         |
| Key-Value Path | `clickhouse/rw_addresses`         |
| Environment    | `NOC_CLICKHOUSE_RW_ADDRESSES`     |

## db

|                |                     |
| -------------- | ------------------- |
| Default value  | `noc`               |
| YAML Path      | `clickhouse.db`     |
| Key-Value Path | `clickhouse/db`     |
| Environment    | `NOC_CLICKHOUSE_DB` |

## rw_user

|                |                          |
| -------------- | ------------------------ |
| Default value  | `default`                |
| YAML Path      | `clickhouse.rw_user`     |
| Key-Value Path | `clickhouse/rw_user`     |
| Environment    | `NOC_CLICKHOUSE_RW_USER` |

## rw_password

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `None`                       |
| YAML Path      | `clickhouse.rw_password`     |
| Key-Value Path | `clickhouse/rw_password`     |
| Environment    | `NOC_CLICKHOUSE_RW_PASSWORD` |

## ro_addresses

|                |                                   |
| -------------- | --------------------------------- |
| Default value  | `service="clickhouse", wait=True` |
| YAML Path      | `clickhouse.ro_addresses`         |
| Key-Value Path | `clickhouse/ro_addresses`         |
| Environment    | `NOC_CLICKHOUSE_RO_ADDRESSES`     |

## ro_user

|                |                          |
| -------------- | ------------------------ |
| Default value  | `readonly`               |
| YAML Path      | `clickhouse.ro_user`     |
| Key-Value Path | `clickhouse/ro_user`     |
| Environment    | `NOC_CLICKHOUSE_RO_USER` |

## ro_password

|                |                              |
| -------------- | ---------------------------- |
| Default value  | `None`                       |
| YAML Path      | `clickhouse.ro_password`     |
| Key-Value Path | `clickhouse/ro_password`     |
| Environment    | `NOC_CLICKHOUSE_RO_PASSWORD` |

## request_timeout

|                |                                  |
| -------------- | -------------------------------- |
| Default value  | `1h`                             |
| YAML Path      | `clickhouse.request_timeout`     |
| Key-Value Path | `clickhouse/request_timeout`     |
| Environment    | `NOC_CLICKHOUSE_REQUEST_TIMEOUT` |

## connect_timeout

|                |                                  |
| -------------- | -------------------------------- |
| Default value  | `10s`                            |
| YAML Path      | `clickhouse.connect_timeout`     |
| Key-Value Path | `clickhouse/connect_timeout`     |
| Environment    | `NOC_CLICKHOUSE_CONNECT_TIMEOUT` |

## default_merge_tree_granularity

|                |                                                 |
| -------------- | ----------------------------------------------- |
| Default value  | `8192`                                          |
| YAML Path      | `clickhouse.default_merge_tree_granularity`     |
| Key-Value Path | `clickhouse/default_merge_tree_granularity`     |
| Environment    | `NOC_CLICKHOUSE_DEFAULT_MERGE_TREE_GRANULARITY` |

## encoding

Default value
:

Possible values
:

-

- deflate
- gzip

YAML Path
: clickhouse.encoding

Key-Value Path
: clickhouse/encoding

Environment
: NOC_CLICKHOUSE_ENCODING

## enable_low_cardinality

|                |                                         |
| -------------- | --------------------------------------- |
| Default value  | `False`                                 |
| YAML Path      | `clickhouse.enable_low_cardinality`     |
| Key-Value Path | `clickhouse/enable_low_cardinality`     |
| Environment    | `NOC_CLICKHOUSE_ENABLE_LOW_CARDINALITY` |

## cluster

|                |                          |
| -------------- | ------------------------ |
| Default value  | ``                       |
| YAML Path      | `clickhouse.cluster`     |
| Key-Value Path | `clickhouse/cluster`     |
| Environment    | `NOC_CLICKHOUSE_CLUSTER` |

## cluster_topology

|                |                                   |
| -------------- | --------------------------------- |
| Default value  | `1`                               |
| YAML Path      | `clickhouse.cluster_topology`     |
| Key-Value Path | `clickhouse/cluster_topology`     |
| Environment    | `NOC_CLICKHOUSE_CLUSTER_TOPOLOGY` |

Examples:

| Value | Description                                                                      |
| ----- | -------------------------------------------------------------------------------- |
| 1     | non-replicated, non-sharded configuration                                        |
| 1,1   | 2 shards, non-replicated                                                         |
| 2,2   | 2 shards, 2 replicas in each                                                     |
| 3:2,2 | first shard has 2 replicas an weight 3, second shard has 2 replicas and weight 1 |
