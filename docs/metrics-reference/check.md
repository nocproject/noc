# Check

Scope for Diagnostic check metrics.

## Table Structure
The `Check` metric scope is stored
in the `check` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| agent | pm.Agent |
| service | sa.Service |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::diagnostic::*` |  | diagnostic_name |
| `noc::check::name::*` |  | check_name |
| `noc::check::arg0::*` | check_arg0 |  |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |
| <a id="check-result"></a>result | UInt64 | Check \| Result | Check result | bool | 1 | 1 |
| <a id="check-status"></a>status | UInt8 | Check \| Status | Check result - yes or no | None | 1 | 1 |