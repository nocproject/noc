# [scheduler] section

[Scheduler](../services/scheduler.md) service configuration

## max_threads

|                |                             |
| -------------- | --------------------------- |
| Default value  | `20`                        |
| YAML Path      | `scheduler.max_threads`     |
| Key-Value Path | `scheduler/max_threads`     |
| Environment    | `NOC_SCHEDULER_MAX_THREADS` |

## submit_threshold_factor

|                |                                         |
| -------------- | --------------------------------------- |
| Default value  | `10`                                    |
| YAML Path      | `scheduler.submit_threshold_factor`     |
| Key-Value Path | `scheduler/submit_threshold_factor`     |
| Environment    | `NOC_SCHEDULER_SUBMIT_THRESHOLD_FACTOR` |

## max_chunk_factor

|                |                                  |
| -------------- | -------------------------------- |
| Default value  | `1`                              |
| YAML Path      | `scheduler.max_chunk_factor`     |
| Key-Value Path | `scheduler/max_chunk_factor`     |
| Environment    | `NOC_SCHEDULER_MAX_CHUNK_FACTOR` |

## updates_per_check

|                |                                   |
| -------------- | --------------------------------- |
| Default value  | `4`                               |
| YAML Path      | `scheduler.updates_per_check`     |
| Key-Value Path | `scheduler/updates_per_check`     |
| Environment    | `NOC_SCHEDULER_UPDATES_PER_CHECK` |

## cache_default_ttl

|                |                                   |
| -------------- | --------------------------------- |
| Default value  | `1d`                              |
| YAML Path      | `scheduler.cache_default_ttl`     |
| Key-Value Path | `scheduler/cache_default_ttl`     |
| Environment    | `NOC_SCHEDULER_CACHE_DEFAULT_TTL` |

## autointervaljob_interval

|                |                                          |
| -------------- | ---------------------------------------- |
| Default value  | `1d`                                     |
| YAML Path      | `scheduler.autointervaljob_interval`     |
| Key-Value Path | `scheduler/autointervaljob_interval`     |
| Environment    | `NOC_SCHEDULER_AUTOINTERVALJOB_INTERVAL` |

## autointervaljob_initial_submit_interval

|                |                                                         |
| -------------- | ------------------------------------------------------- |
| Default value  | `1d`                                                    |
| YAML Path      | `scheduler.autointervaljob_initial_submit_interval`     |
| Key-Value Path | `scheduler/autointervaljob_initial_submit_interval`     |
| Environment    | `NOC_SCHEDULER_AUTOINTERVALJOB_INITIAL_SUBMIT_INTERVAL` |
