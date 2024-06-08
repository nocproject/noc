# How to backup NOC

All instructions are for singlenode installation.

## Creating Backup

It's necessary to do backup of both databases(MongoDB + PostgreSQL) simultaneously due to complex links between data.
1. Stop NOC services: `systemctl stop noc`
2. Do backups:
   * mongod: `mongodump --db=noc --username=noc --password=noc -v --out=/backup/mongodump/ --gzip`
   * postgresql: `sudo -u postgres pg_dumpall -c -f /backup/pg_dumpall.out -v -U postgres`
   * clickhouse: look at this [link](https://clickhouse.com/docs/en/operations/backup) or just backup the `/var/lib/clickhouse/` if you want to save metrics
3. Start NOC services: `systemctl start noc`

## Restoring Backup

1. Empty databases and then load them with your data
2. Stop NOC services: `systemctl stop noc`
3. MongoDB:
   * `cd /opt/noc/ && ./noc mongo`
   * `db.dropDatabase();`
   * `mongorestore --db=noc --username=noc --password=noc --gzip mongo_noc/noc/`

4. Postgres:
   * `sudo -u postgres psql`
   * `drop database noc;` (all postgres clients should be stopped: noc, pgbouncer, grafana-server)
   * `sudo -u postgres psql -f pg_dumpall.out`

## VM Backup

Virtual Machine backup is also an acceptable option, but it may not be file consistent as direct DB backup.
