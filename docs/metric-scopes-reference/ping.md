---
uuid: b74189ad-3b8d-43d3-9d84-06d46f379674
---
# Ping Metric Scope

Ping-related metrics

## Data Table

ClickHouse Table: `ping`

| Field                                                  | Type     | Description                                                    |
| ------------------------------------------------------ | -------- | -------------------------------------------------------------- |
| date                                                   | Date     | Measurement Date                                               |
| ts                                                     | DateTime | Measurement Timestamp                                          |
| [attempts](../metric-types-reference/ping/attempts.md) | UInt16   | [Ping \| Attempts](../metric-types-reference/ping/attempts.md) |
| [rtt](../metric-types-reference/ping/rtt.md)           | UInt32   | [Ping \| RTT](../metric-types-reference/ping/rtt.md)           |
