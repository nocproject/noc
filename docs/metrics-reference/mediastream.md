# MediaStream

Metrics for Video/Audio Streams

## Table Structure
The `MediaStream` metric scope is stored
in the `mediastream` ClickHouse table.

Key Fields:

| Field Name | Model |
| --- | --- |
| managed_object | sa.ManagedObject |
| object | inv.Object |


Label Mappings:

| Label | View Column | Store Column |
| --- | --- | --- |
| `noc::media::stream::*` | stream | stream |
| `noc::media::channel::*` | channel |  |
| `noc::media::view::*` | view |  |


Data Fields:

| Field | Type | Metric Type | Description | Measure | Units | Scale |
| --- | --- | --- | --- | --- | --- | --- |