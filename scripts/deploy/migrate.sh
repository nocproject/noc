#!/bin/sh
python manage.py syncdb --noinput
python manage.py migrate
python manage.py sync-perm
if [ ! -z "$(getent hosts clickhouse)" ]; then
     python commands/migrate-ch.py
fi
python ./scripts/deploy/install-packages requirements/collections.json && python commands/collection.py sync