# Как бекапить NOC

Все инструкции для однонодовой инсталляции

## Создание бекапа

Важно производить бекап обоих баз одновременно(MongoDB + PostgreSQL) из-за перекрёстных связей между содержимым.
1. Остановить NOC: `systemctl stop noc`
2. Произвести бекап:
   * mongod: `mongodump --db=noc --username=noc --password=noc -v --out=/backup/mongodump/ --gzip`
   * postgresql: `sudo -u postgres pg_dumpall -c -f /backup/pg_dumpall.out -v -U postgres`
   * clickhouse: смотри [сюда](https://clickhouse.com/docs/en/operations/backup) или сохрани `/var/lib/clickhouse/` если хочешь сохранить историю метрик.
3. Запустить NOC: `systemctl start noc`

## Восстановление из бекапа

1. Очистить содержимое БД и наполнить их данными из бекапа
2. Остановить NOC: `systemctl stop noc`
3. MongoDB:
   * `cd /opt/noc/ && ./noc mongo`
   * `db.dropDatabase();`
   * `mongorestore --db=noc --username=noc --password=noc --gzip mongo_noc/noc/`

4. Postgres:
   * `sudo -u postgres psql`
   * `drop database noc;` (все потенциальные клиенты бд должны быть остановлены: noc, pgbouncer, grafana-server)
   * `sudo -u postgres psql -f pg_dumpall.out`

## Бекап VM

Бекап на уровне виртуальной машины (VM) приемлем, но есть малая возможность получить неконсистентный бекап.
