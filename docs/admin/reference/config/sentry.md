# [sentry] section

Sentry service configuration

## url

|                |                  |
| -------------- | ---------------- |
| Default value  | ``               |
| YAML Path      | `sentry.url`     |
| Key-Value Path | `sentry/url`     |
| Environment    | `NOC_SENTRY_URL` |

## shutdown_timeout

Default value
: 2

Possible values
: 1..10

YAML Path
: sentry.shutdown_timeout

Key-Value Path
: sentry/shutdown_timeout

Environment
: NOC_SENTRY_SHUTDOWN_TIMEOUT

## default_integrations

|                |                                   |
| -------------- | --------------------------------- |
| Default value  | `False`                           |
| YAML Path      | `sentry.default_integrations`     |
| Key-Value Path | `sentry/default_integrations`     |
| Environment    | `NOC_SENTRY_DEFAULT_INTEGRATIONS` |

## debug

|                |                    |
| -------------- | ------------------ |
| Default value  | `False`            |
| YAML Path      | `sentry.debug`     |
| Key-Value Path | `sentry/debug`     |
| Environment    | `NOC_SENTRY_DEBUG` |

## max_breadcrumbs

Default value
: 10

Possible values
: 1..100

YAML Path
: sentry.max_breadcrumbs

Key-Value Path
: sentry/max_breadcrumbs

Environment
: NOC_SENTRY_MAX_BREADCRUMBS
