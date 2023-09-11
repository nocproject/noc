# ch.TABLE Stream

`ch.TABLE` streams pass messages from data producers to
the chwriter services, which writes them into ClickHouse database.
Each ClickHouse table has own `ch.TABLE` stream, i.e. `interfaces` table
uses `ch.interface` stream, while `macs` table uses `ch.macs` stream.

## Publishers

- [discovery](../../../admin/reference/services/discovery.md) service.
- [syslogcollector](../../../admin/reference/services/syslogcollector.md) service.
- Any service providing Span telemetry.
- `./noc bi load` command.

## Subscribers

- [chwriter](../../../admin/reference/services/chwriter.md) service.

## Message Headers

`ch.TABLE` stream doesn't use additional headers.

## Message Format

`ch.TABLE` streams holds newline-separated JSON objects, i.e. JSONEachRow
ClickHouse format

## Partitioning

Each ClickHouse shard has separate partition. Non-sharded installations
utilize single partition.
