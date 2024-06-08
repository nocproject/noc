# SLA

SLA-related metrics

## Table Structure
The `SLA` metric scope is stored
in the `sla` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |
| sla_probe | sla.SLAProbe |
| service | sa.Service |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::sla::group::*` |  | group |
| `noc::sla::name::*` |  | name |
| `noc::sla::tag::*` |  |  |
| `noc::sla::target::*` |  |  |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="sla-icmp-rtt"></a>icmp_rtt | UInt32 | SLA \| ICMP RTT | Measured round trip time for ICMP packets in microseconds | μs | s | u |
| <a id="sla-jitter"></a>jitter | Int32 | SLA \| JITTER | Measured deviation of round trip time in microseconds | μs | s | u |
| <a id="sla-jitter-avg"></a>jitter_avg | Int32 | SLA \| Jitter \| Avg | The average of positive and negative jitter values in SD and DS direction for latest operation. | μs | s | u |
| <a id="sla-jitter-icpif"></a>jitter_icpif | Int32 | SLA \| Jitter \| ICPIF | Represents ICPIF value for the latest jitter operation. This value will be 93 for packet loss of 10% or more. | * | 1 | 1 |
| <a id="sla-jitter-in-avg"></a>jitter_in_avg | Int32 | SLA \| Jitter \| In \| Avg | The average of positive and negative jitter values from destination to source for latest operation. | μs | s | u |
| <a id="sla-jitter-mos"></a>jitter_mos | Int16 | SLA \| Jitter \| MOS | The MOS (Mean Opinion Score) value for the latest jitter test.  | * | 1 | 1 |
| <a id="sla-jitter-out-avg"></a>jitter_out_avg | Int32 | SLA \| Jitter \| Out \| Avg | The average of positive and negative jitter values from source to destination for latest operation. | μs | s | u |
| <a id="sla-loss"></a>loss | UInt32 | SLA \| LOSS | Actual number of lost packets | int | pkt | 1 |
| <a id="sla-octets-in"></a>octets_in | UInt64 | SLA \| Octets \| In | The total number of octets received on the test, including framing characters.  | bytes | byte | 1 |
| <a id="sla-octets-out"></a>octets_out | UInt64 | SLA \| Octets \| Out | The total number of octets send on the test, including framing characters.  | bytes | byte | 1 |
| <a id="sla-onewaylatency-in-max"></a>owl_in_max | UInt32 | SLA \| OneWayLatency \| In \| Max |  The maximum of all OWD (One Way Delay) from destination to source. | * | s | u |
| <a id="sla-onewaylatency-out-max"></a>owl_out_max | UInt32 | SLA \| OneWayLatency \| Out \| Max | The maximum of all OWD (One Way Delay/Latency) from source to destination. | * | s | u |
| <a id="sla-packets"></a>packets_count | UInt32 | SLA \| Packets |  The number of packets (probes) sent in the test. | * | pkt | 1 |
| <a id="sla-packets-disordered"></a>packets_disordered_count | UInt32 | SLA \| Packets \| Disordered | The number of packets arrived out of sequence. | pp | pkt | 1 |
| <a id="sla-packets-in"></a>packets_in | UInt64 | SLA \| Packets \| In | The number of packets received in the test. | * | pkt | 1 |
| <a id="sla-packets-loss-in"></a>packets_loss_in | UInt32 | SLA \| Packets \| Loss \| In | The number of packets lost when sent from destination to source. | pp | pkt | 1 |
| <a id="sla-packets-loss-in-ratio"></a>packets_loss_in_ratio | UInt16 | SLA \| Packets \| Loss \| In \| Ratio | The ratio of the packets lost to all packets sent from destination to source. | % | % | 1 |
| <a id="sla-packets-loss-out"></a>packets_loss_out | UInt32 | SLA \| Packets \| Loss \| Out | The number of packets lost when sent from source to destination. | pp | pkt | 1 |
| <a id="sla-packets-loss-out-ratio"></a>packets_loss_out_ratio | UInt16 | SLA \| Packets \| Loss \| Out \| Ratio | The ratio of the packets lost to all packets sent from source to destination. | % | % | 1 |
| <a id="sla-packets-loss-ratio"></a>packets_loss_ratio | UInt16 | SLA \| Packets \| Loss \| Ratio | The ratio of the packets lost to all packets sent in a test. | % | % | 1 |
| <a id="sla-packets-out"></a>packets_out | UInt64 | SLA \| Packets \| Out | The number of packets sent in the test. | * | pkt | 1 |
| <a id="sla-packets-rate-in"></a>packets_rate_in | UInt64 | SLA \| Packets \| Rate \| In | SLA test packets input throughput | bit/s | pps | 1 |
| <a id="sla-packets-rate-out"></a>packets_rate_out | UInt64 | SLA \| Packets \| Rate \| Out | SLA test packets output throughput | bit/s | pps | 1 |
| <a id="sla-probes-error"></a>probes_error | UInt32 | SLA \| Probes \| Error | The number of occasions when a jitter operation could not be initiated because an internal error | * | 1 | 1 |
| <a id="sla-rate-in"></a>rate_in | UInt64 | SLA \| Rate \| In | SLA test input throughput | bit/s | bit/s | 1 |
| <a id="sla-rate-out"></a>rate_out | UInt64 | SLA \| Rate \| Out | SLA test output throughput | bit/s | bit/s | 1 |
| <a id="sla-rtt-max"></a>rtt_max | UInt32 | SLA \| RTT \| Max | The maximum of RTT's that were successfully measured | μs | s | u |
| <a id="sla-rtt-min"></a>rtt_min | UInt32 | SLA \| RTT \| Min | The minimum of RTT's that were successfully measured | μs | s | u |
| <a id="sla-duration"></a>test_duration | UInt64 | SLA \| Duration | Test duration time | s | s | u |
| <a id="sla-test-status"></a>test_status | UInt16 | SLA \| Test \| Status | None | s | 1 | 1 |
| <a id="sla-twowaylatency-in-avg"></a>twl_in_avg | UInt64 | SLA \| TwoWayLatency \| In \| Avg | The average of all TWD (Two Way Delay) from destination to source. | * | s | u |
| <a id="sla-twowaylatency-in-max"></a>twl_in_max | UInt64 | SLA \| TwoWayLatency \| In \| Max | The maximum of all TWD (Two Way Delay) from destination to source. | * | s | u |
| <a id="sla-twowaylatency-in-min"></a>twl_in_min | UInt64 | SLA \| TwoWayLatency \| In \| Min | The minimum of all TWD (Two Way Delay) from destination to source. | * | s | u |
| <a id="sla-twowaylatency-out-avg"></a>twl_out_avg | UInt64 | SLA \| TwoWayLatency \| Out \| Avg | The average of all TWD (Two Way Delay/Latency) from source to destination. | * | s | u |
| <a id="sla-twowaylatency-out-max"></a>twl_out_max | UInt64 | SLA \| TwoWayLatency \| Out \| Max | The maximum of all TWD (Two Way Delay/Latency) from source to destination. | * | s | u |
| <a id="sla-twowaylatency-out-min"></a>twl_out_min | UInt64 | SLA \| TwoWayLatency \| Out \| Min | The minimum of all TWD (Two Way Delay/Latency) from source to destination. | * | s | u |
| <a id="sla-udp-rtt"></a>udp_rtt | UInt32 | SLA \| UDP RTT | Measured round trip time for UDP packets in microseconds | μs | s | u |