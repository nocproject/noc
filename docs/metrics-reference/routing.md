# Routing

Scope for L2/L3 protocols metrics

## Table Structure
The `Routing` metric scope is stored
in the `routing` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::vr::*` | vr |  |
| `noc::instance::*` | instance |  |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="network-stp-topology-changes"></a>stp_topology_changes | UInt32 | Network \| STP \| Topology Changes | The total number of topology changes detected by this bridge since the management entity was last reset or initialized. | C | 1 | 1 |
| <a id="network-stp-topology-changes-delta"></a>stp_topology_changes_delta | UInt32 | Network \| STP \| Topology Changes \| Delta | The delta of topology changes detected by this bridge since the management entity was last collect. | C | 1 | 1 |
| <a id="network-stp-topology-changes-rate"></a>stp_topology_changes_rate | UInt32 | Network \| STP \| Topology Changes \| Rate | The rate of topology changes detected by this bridge. | None | 1 | 1 |