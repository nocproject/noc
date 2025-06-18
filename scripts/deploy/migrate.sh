#!/bin/sh
# Perform all migrations
set -e
if [ -n "$NOC_MIGRATE_SLOTS_PATH" ]; then
    if [ -d "$NOC_MIGRATE_SLOTS_PATH" ]; then
        ./noc dcs set-slots -f $NOC_MIGRATE_SLOTS_PATH/*
    else 
        ./noc dcs set-slots -f $NOC_MIGRATE_SLOTS_PATH
    fi
fi
./noc migrate
./noc ensure-indexes
./noc migrate-liftbridge
./noc collection sync
./noc migrate-liftbridge
./noc migrate-ch
./noc sync-perm
echo "# Syncing MIB"
./noc sync-mibs
