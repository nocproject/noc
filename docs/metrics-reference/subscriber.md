# Subscriber

Subscriber-related metrics

## Table Structure
The `Subscriber` metric scope is stored
in the `subscriber` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::chassis::*` |  |  |
| `noc::slot::*` | slot |  |
| `noc::module::*` | module |  |
| `noc::interface::*` | interface |  |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="subscribers-ipoe"></a>ipoe | UInt32 | Subscribers \| IPoE | Total active IPoE sessions on the box | sessions | 1 | 1 |
| <a id="subscribers-l2tp"></a>l2tp | UInt32 | Subscribers \| L2TP | Total active L2TP sessions on the box | sessions | 1 | 1 |
| <a id="subscribers-ppp"></a>ppp | UInt32 | Subscribers \| PPP | Total active PPP sessions on the box | sessions | 1 | 1 |
| <a id="subscribers-pppoe"></a>pppoe | UInt32 | Subscribers \| PPPoE | Total active PPPoE sessions on the box | sessions | 1 | 1 |
| <a id="subscribers-pptp"></a>pptp | UInt32 | Subscribers \| PPTP | Total active PPTP sessions on the box | sessions | 1 | 1 |
| <a id="subscribers-summary"></a>summary | UInt32 | Subscribers \| Summary | Total active sessions on the box | sessions | 1 | 1 |