# [features] section

Features service configuration

## use_uvloop

{{ config_param("features.use_uvloop") }}

## cp

{{ config_param("features.cp") }}

## sentry

{{ config_param("features.sentry") }}

## cpclient

{{ config_param("features.cpclient") }}

## telemetry

Enable internal telemetry export to Clickhouse

{{ config_param("features.telemetry") }}

## consul_healthchecks

While registering serive in consul also register health check

{{ config_param("features.consul_healthchecks") }}

## service_registration

Permit consul self registration

{{ config_param("features.service_registration") }}

## forensic

{{ config_param("features.forensic") }}

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
