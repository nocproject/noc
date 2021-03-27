---
uuid: b74189ad-3b8d-43d3-9d84-06d46f379674
---
# Ping Metric Scope

Ping-related metrics

## Data Table

ClickHouse Table: `ping`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
[attempts](../types/ping/attempts.md) | UInt16 | [Ping \| Attempts](../types/ping/attempts.md)
[rtt](../types/ping/rtt.md) | UInt32 | [Ping \| RTT](../types/ping/rtt.md)
