# PhonePeer

Scope for Phone Peer protocols metrics (SIP Trunk, E1 Serial, etc.) . Explain:
trunk as interface
channel as subinterface

## Table Structure
The `PhonePeer` metric scope is stored
in the `phonepeer` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::phone::trunk::*` | trunk |  |
| `noc::phone::channel::*` | channel |  |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |