# Feature Gates Reference

Feature gates control optional system functionality that can be selectively enabled or disabled.
They provide early access to new capabilities and allow testing of experimental features before they are fully stabilized.

Feature gates are configured via the features.gate parameter.

See the [configuration reference](../config-reference/features.md#gate) for details.

Example:
``` yaml
features:
    gate: channel,jobs
```

## States

Each feature can be in one of the following states:

- **ALFA:** Experimental and highly unstable. Do not enable unless you're fully aware of the risks.
- **BETA:** Under active development and testing. Enable only if you need to evaluate it in a controlled environment.
- **MATURE:** Stable and production-ready. May be enabled or disabled based on your use case.


## Available Features

### channel

Enables channel management.

- **Status**: ALFA
- **Available since**: 25.1

### jobs

Enables the orchestrator framework.

- **Status**: ALFA
- **Available since**: 25.1