---
uuid: c2cb029b-4cda-4187-b92b-386c27ea561f
---
# SLA Metric Scope

SLA-related metrics

## Data Table

ClickHouse Table: `sla`

| Field                                                 | Type                          | Description                                                  |
| ----------------------------------------------------- | ----------------------------- | ------------------------------------------------------------ |
| date                                                  | Date                          | Measurement Date                                             |
| ts                                                    | DateTime                      | Measurement Timestamp                                        |
| path                                                  | Array of String {{ complex }} | Measurement Path                                             |
| {{ tab }} `probe`                                     | {{ no }}                      |
| {{ tab }} `test`                                      | {{ no }}                      |
| [icmp_rtt](../metric-types-reference/sla/icmp-rtt.md) | UInt32                        | [SLA \| ICMP RTT](../metric-types-reference/sla/icmp-rtt.md) |
| [jitter](../metric-types-reference/sla/jitter.md)     | Int32                         | [SLA \| JITTER](../metric-types-reference/sla/jitter.md)     |
| [loss](../metric-types-reference/sla/loss.md)         | UInt32                        | [SLA \| LOSS](../metric-types-reference/sla/loss.md)         |
| [udp_rtt](../metric-types-reference/sla/udp-rtt.md)   | UInt32                        | [SLA \| UDP RTT](../metric-types-reference/sla/udp-rtt.md)   |
