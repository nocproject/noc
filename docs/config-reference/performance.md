# [performance] section

Metrics service configuration

## default_hist

|                |                                                   |
| -------------- | ------------------------------------------------- |
| Default value  | `[0.001, 0.005, 0.01, 0.05, 0.5, 1.0, 5.0, 10.0]` |
| YAML Path      | `metrics.default_hist`                            |
| Key-Value Path | `metrics/default_hist`                            |
| Environment    | `NOC_METRICS_DEFAULT_HIST`                        |

## enable_mongo_hist

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `False`                         |
| YAML Path      | `metrics.enable_mongo_hist`     |
| Key-Value Path | `metrics/enable_mongo_hist`     |
| Environment    | `NOC_METRICS_ENABLE_MONGO_HIST` |

## mongo_hist

|                |                                                   |
| -------------- | ------------------------------------------------- |
| Default value  | `[0.001, 0.005, 0.01, 0.05, 0.5, 1.0, 5.0, 10.0]` |
| YAML Path      | `metrics.mongo_hist`                              |
| Key-Value Path | `metrics/mongo_hist`                              |
| Environment    | `NOC_METRICS_MONGO_HIST`                          |

## enable_postgres_hist

|                |                                    |
| -------------- | ---------------------------------- |
| Default value  | `False`                            |
| YAML Path      | `metrics.enable_postgres_hist`     |
| Key-Value Path | `metrics/enable_postgres_hist`     |
| Environment    | `NOC_METRICS_ENABLE_POSTGRES_HIST` |

## postgres_hist

|                |                                                   |
| -------------- | ------------------------------------------------- |
| Default value  | `[0.001, 0.005, 0.01, 0.05, 0.5, 1.0, 5.0, 10.0]` |
| YAML Path      | `metrics.postgres_hist`                           |
| Key-Value Path | `metrics/postgres_hist`                           |
| Environment    | `NOC_METRICS_POSTGRES_HIST`                       |

## default_quantiles

|                |                                 |
| -------------- | ------------------------------- |
| Default value  | `[0.5, 0.9, 0.95]`              |
| YAML Path      | `metrics.default_quantiles`     |
| Key-Value Path | `metrics/default_quantiles`     |
| Environment    | `NOC_METRICS_DEFAULT_QUANTILES` |

## default_quantiles_epsilon

Acceptable ranking error for approximate quantiles calculation.

Consider we have 1000 measurements and calculating 2-nd quartile (50% or 0.5).
Exact quantile calculation must return `1000 * 0.5 = 500` item
of ordered list of measurement but we need to keep all 1000 measurements
in memory.

Approximate quantiles calculation guaranted to return an item between
`1000 * (0,5 - Epsilon)` and `1000 * (0.5 + Epsilon). So for default value of 0.01 value between`490`and`510` position will be returned,
greatly relaxing memory requirements.

Lesser values means greater precision and greater memory and cpu requirements,
while greater values means lesser precision but lesser memory and cpu penalty.

|                |                                         |
| -------------- | --------------------------------------- |
| Default value  | `0.01`                                  |
| YAML Path      | `metrics.default_quantiles_epsilon`     |
| Key-Value Path | `metrics/default_quantiles_epsilon`     |
| Environment    | `NOC_METRICS_DEFAULT_QUANTILES_EPSILON` |

## default_quantiles_window

Quantiles window size in seconds. NOC maintains 2 quantile windows -
temporary and active one, purging active and swapping windows
every `default_quantiles_window` seconds.

|                |                                        |
| -------------- | -------------------------------------- |
| Default value  | `60`                                   |
| YAML Path      | `metrics.default_quantiles_window`     |
| Key-Value Path | `metrics/default_quantiles_window`     |
| Environment    | `NOC_METRICS_DEFAULT_QUANTILES_WINDOW` |

## default_quantiles_buffer

|                |                                        |
| -------------- | -------------------------------------- |
| Default value  | `100`                                  |
| YAML Path      | `metrics.default_quantiles_buffer`     |
| Key-Value Path | `metrics/default_quantiles_buffer`     |
| Environment    | `NOC_METRICS_DEFAULT_QUANTILES_BUFFER` |

## enable_mongo_quantiles

Enable quantiles collection for mongo transactions

|                |                                      |
| -------------- | ------------------------------------ |
| Default value  | `False`                              |
| YAML Path      | `metrics.enable_mongo_quantiles`     |
| Key-Value Path | `metrics/enable_mongo_quantiles`     |
| Environment    | `NOC_METRICS_ENABLE_MONGO_QUANTILES` |

## enable_postgres_quantiles

Enable quantiles collection for postgresql transactions

|                |                                         |
| -------------- | --------------------------------------- |
| Default value  | `False`                                 |
| YAML Path      | `metrics.enable_postgres_quantiles`     |
| Key-Value Path | `metrics/enable_postgres_quantiles`     |
| Environment    | `NOC_METRICS_ENABLE_POSTGRES_QUANTILES` |
