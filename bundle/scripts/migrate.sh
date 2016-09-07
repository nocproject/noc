#!/bin/sh

echo "Launching syncdb --noinput"
./noc syncdb --noinput
echo "Launching migrate --ignore-ghost-migrations"
./noc migrate --ignore-ghost-migrations
echo "Launching sync-perm"
./noc sync-perm
Echo "Launching collection sync"
./noc collection sync
echo "Launching sync-mibs"
./noc sync-mibs
