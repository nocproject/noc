#!/bin/sh

echo "Launching syncdb --noinput"
./noc syncdb --noinput
echo "Launching migrate --ignore-ghost-migrations"
./noc migrate --ignore-ghost-migrations
echo "Launching collection sync"
./noc collection sync
echo "Launching sync-perm"
./noc sync-mibs
