# [nbi] section

[Nbi](../services/nbi.md) service configuration

## max_threads

NBI process' threadpool size. Roughly - amount of concurrent
requests can be served by single `nbi<services-nbi>` instance.

|                |                       |
| -------------- | --------------------- |
| Default value  | `10`                  |
| YAML Path      | `nbi.max_threads`     |
| Key-Value Path | `nbi/max_threads`     |
| Environment    | `NOC_NBI_MAX_THREADS` |

## objectmetrics_max_interval

Maximal time span (in seconds) which can be requested via
`NBI objectmetrics API<api-nbi-objectmetrics>`.

|                |                                      |
| -------------- | ------------------------------------ |
| Default value  | `3h`                                 |
| YAML Path      | `nbi.objectmetrics_max_interval`     |
| Key-Value Path | `nbi/objectmetrics_max_interval`     |
| Environment    | `NOC_NBI_OBJECTMETRICS_MAX_INTERVAL` |
