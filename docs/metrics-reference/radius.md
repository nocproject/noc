# Radius

Radius protocols related metrics

## Table Structure
The `Radius` metric scope is stored
in the `radius` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |
| service | sa.Service |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::radius::*` |  | name |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="radius-policy-request-count"></a>radius_policy_request_count | UInt32 | Radius \| Policy \| Request \| Count | The number of RADIUS request packets transmitted | None | 1 | 1 |
| <a id="radius-policy-request-delta"></a>radius_policy_request_delta | UInt32 | Radius \| Policy \| Request \| Delta | The number of RADIUS request packets transmitted | None | 1 | 1 |
| <a id="radius-policy-response-count"></a>radius_policy_response_count | UInt32 | Radius \| Policy \| Response \| Count | The number of RADIUS request packets transmitted | None | 1 | 1 |
| <a id="radius-policy-response-delta"></a>radius_policy_response_delta | UInt32 | Radius \| Policy \| Response \| Delta | The number of RADIUS request packets transmitted | None | 1 | 1 |