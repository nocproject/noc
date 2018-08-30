#!/bin/sh
set -e
./noc migrate
./noc sync-perm
if [ ! -z "$(getent hosts clickhouse)" ]; then
     ./noc migrate-ch
fi
python ./scripts/deploy/install-packages requirements/collections.json && ./noc collection sync
