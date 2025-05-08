# [features] section

Features service configuration

## use_uvloop

|                |                           |
| -------------- | ------------------------- |
| Default value  | `False`                   |
| YAML Path      | `features.use_uvloop`     |
| Key-Value Path | `features/use_uvloop`     |
| Environment    | `NOC_FEATURES_USE_UVLOOP` |

## cp

|                |                   |
| -------------- | ----------------- |
| Default value  | `True`            |
| YAML Path      | `features.cp`     |
| Key-Value Path | `features/cp`     |
| Environment    | `NOC_FEATURES_CP` |

## sentry

|                |                       |
| -------------- | --------------------- |
| Default value  | `False`               |
| YAML Path      | `features.sentry`     |
| Key-Value Path | `features/sentry`     |
| Environment    | `NOC_FEATURES_SENTRY` |

## traefik

|                |                        |
| -------------- | ---------------------- |
| Default value  | `False`                |
| YAML Path      | `features.traefik`     |
| Key-Value Path | `features/traefik`     |
| Environment    | `NOC_FEATURES_TRAEFIK` |

## cpclient

|                |                         |
| -------------- | ----------------------- |
| Default value  | `False`                 |
| YAML Path      | `features.cpclient`     |
| Key-Value Path | `features/cpclient`     |
| Environment    | `NOC_FEATURES_CPCLIENT` |

## telemetry

Enable internal telemetry export to Clickhouse

|                |                          |
| -------------- | ------------------------ |
| Default value  | `False`                  |
| YAML Path      | `features.telemetry`     |
| Key-Value Path | `features/telemetry`     |
| Environment    | `NOC_FEATURES_TELEMETRY` |

## consul_healthchecks

While registering serive in consul also register health check

|                |                                    |
| -------------- | ---------------------------------- |
| Default value  | `True`                             |
| YAML Path      | `features.consul_healthchecks`     |
| Key-Value Path | `features/consul_healthchecks`     |
| Environment    | `NOC_FEATURES_CONSUL_HEALTHCHECKS` |

## service_registration

Permit consul self registration

|                |                                     |
| -------------- | ----------------------------------- |
| Default value  | `True`                              |
| YAML Path      | `features.service_registration`     |
| Key-Value Path | `features/service_registration`     |
| Environment    | `NOC_FEATURES_SERVICE_REGISTRATION` |

## forensic

|                |                         |
| -------------- | ----------------------- |
| Default value  | `False`                 |
| YAML Path      | `features.forensic`     |
| Key-Value Path | `features/forensic`     |
| Environment    | `NOC_FEATURES_FORENSIC` |

## gate

Enables or disables specific features using the [Feature Gates](../feature-gates-reference/index.md).
Specify a list of feature names. To explicitly disable a feature,
prefix its name with a `-`.

Example:
``` yaml
features:
    gate:
        - channel
        - -jobs
```

{{ config_param("features.gate") }}