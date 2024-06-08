# [topo] section

[Topo](../services-reference/topo.md) service configuration

## dry_run

Do not write topology to database when set.

|                |                    |
| -------------- | ------------------ |
| Default value  | `True`             |
| YAML Path      | `topo.dry_run`     |
| Key-Value Path | `topo/dry_run`     |
| Environment    | `NOC_TOPO_DRY_RUN` |

## check

Additionally check if uplinks are valid
(Lead to adjanced nodes)

|                |                  |
| -------------- | ---------------- |
| Default value  | `False`          |
| YAML Path      | `topo.check`     |
| Key-Value Path | `topo/check`     |
| Environment    | `NOC_TOPO_CHECK` |

## ds_limit

Batch size for datastream client.

|                |                     |
| -------------- | ------------------- |
| Default value  | `1000`              |
| YAML Path      | `topo.ds_limit`     |
| Key-Value Path | `topo/ds_limit`     |
| Environment    | `NOC_TOPO_DS_LIMIT` |

## interval

Topology recalculation interval in seconds.

|                |                     |
| -------------- | ------------------- |
| Default value  | `60`                |
| YAML Path      | `topo.interval`     |
| Key-Value Path | `topo/interval`     |
| Environment    | `NOC_TOPO_INTERVAL` |