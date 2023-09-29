# Ping

Ping-related metrics

## Table Structure
The `Ping` metric scope is stored
in the `ping` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |



Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="ping-attempts"></a>attempts | UInt16 | Ping \| Attempts | ICMP Ping packet loss in per request |  | pkt | 1 |
| <a id="ping-rtt"></a>rtt | UInt32 | Ping \| RTT | ICMP Ping round trip time in microseconds | ms | s | m |