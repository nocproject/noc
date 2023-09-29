# Neighbors

Metrics for L2/L3 protocols neighbors

## Table Structure
The `Neighbors` metric scope is stored
in the `neighbors` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::vr::*` | vr |  |
| `noc::instance::*` | instance |  |
| `noc::neighbor::*` |  | neighbor |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |