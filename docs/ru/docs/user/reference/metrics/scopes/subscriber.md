---
uuid: 7e8c2273-5c24-4692-ae07-0b996d709eec
---
# Subscriber Metric Scope

Subscriber-related metrics

## Data Table

ClickHouse Table: `subscriber`

Field | Type | Description
--- | --- | ---
date | Date | Measurement Date
ts | DateTime | Measurement Timestamp
path | Array of String {{ complex }} | Measurement Path
{{ tab }} `chassis` | {{ no }} | 
{{ tab }} `slot` | {{ no }} | 
{{ tab }} `module` | {{ no }} | 
[ipoe](../types/subscribers/ipoe.md) | UInt32 | [Subscribers \| IPoE](../types/subscribers/ipoe.md)
[l2tp](../types/subscribers/l2tp.md) | UInt32 | [Subscribers \| L2TP](../types/subscribers/l2tp.md)
[ppp](../types/subscribers/ppp.md) | UInt32 | [Subscribers \| PPP](../types/subscribers/ppp.md)
[pppoe](../types/subscribers/pppoe.md) | UInt32 | [Subscribers \| PPPoE](../types/subscribers/pppoe.md)
[pptp](../types/subscribers/pptp.md) | UInt32 | [Subscribers \| PPTP](../types/subscribers/pptp.md)
[summary](../types/subscribers/summary.md) | UInt32 | [Subscribers \| Summary](../types/subscribers/summary.md)
