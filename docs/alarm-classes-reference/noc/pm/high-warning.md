---
uuid: 51c2a38c-82f0-4b85-994c-5369e8834ec5
---
# NOC | PM | High Warning

Alarm Class for high warning thresholds

## Symptoms

Values are out of second threshold value.

## Probable Causes

Metric value cross critical threshold

## Recommended Actions

## Variables

Variable | Description | Default
--- | --- | ---
metric | Metric name | {{ no }}
scope | Metric scope | {{ no }}
path | Path to component raising alarm | {{ no }}
value | Metric value | {{ no }}
threshold | Threshold value | {{ no }}
window_type | Type of window (time or count) | {{ no }}
window | Window size | {{ no }}
window_function | Function apply to window | {{ no }}
