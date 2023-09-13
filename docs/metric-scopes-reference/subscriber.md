---
uuid: 7e8c2273-5c24-4692-ae07-0b996d709eec
---
# Subscriber Metric Scope

Subscriber-related metrics

## Data Table

ClickHouse Table: `subscriber`

| Field                                                       | Type                          | Description                                                                |
| ----------------------------------------------------------- | ----------------------------- | -------------------------------------------------------------------------- |
| date                                                        | Date                          | Measurement Date                                                           |
| ts                                                          | DateTime                      | Measurement Timestamp                                                      |
| path                                                        | Array of String {{ complex }} | Measurement Path                                                           |
| {{ tab }} `chassis`                                         | {{ no }}                      |
| {{ tab }} `slot`                                            | {{ no }}                      |
| {{ tab }} `module`                                          | {{ no }}                      |
| [ipoe](../metric-types-reference/subscribers/ipoe.md)       | UInt32                        | [Subscribers \| IPoE](../metric-types-reference/subscribers/ipoe.md)       |
| [l2tp](../metric-types-reference/subscribers/l2tp.md)       | UInt32                        | [Subscribers \| L2TP](../metric-types-reference/subscribers/l2tp.md)       |
| [ppp](../metric-types-reference/subscribers/ppp.md)         | UInt32                        | [Subscribers \| PPP](../metric-types-reference/subscribers/ppp.md)         |
| [pppoe](../metric-types-reference/subscribers/pppoe.md)     | UInt32                        | [Subscribers \| PPPoE](../metric-types-reference/subscribers/pppoe.md)     |
| [pptp](../metric-types-reference/subscribers/pptp.md)       | UInt32                        | [Subscribers \| PPTP](../metric-types-reference/subscribers/pptp.md)       |
| [summary](../metric-types-reference/subscribers/summary.md) | UInt32                        | [Subscribers \| Summary](../metric-types-reference/subscribers/summary.md) |
