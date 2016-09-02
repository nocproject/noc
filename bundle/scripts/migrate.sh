#!/bin/sh

echo "Launching syncdb --noinput"
./noc syncdb --noinput
echo "Launching migrate --ignore-ghost-migrations"
./noc migrate --ignore-ghost-migrations
echo "Launching sync-perm"
./noc sync-perm
echo "Launching sync-perm"
./noc sync-mibs
