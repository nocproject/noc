#!/bin/sh
# Perform all migrations
set -e
if [ -n "$NOC_MIGRATE_SLOTS_PATH" ]; then
    if [ -d "$NOC_MIGRATE_SLOTS_PATH" ]; then
        ./noc set-slots -f $NOC_MIGRATE_SLOTS_PATH/*
    else 
        ./noc set-slots -f $NOC_MIGRATE_SLOTS_PATH
    fi
fi
./noc migrate
./noc ensure-indexes
./noc migrate-liftbridge
./noc collection sync
./noc miigrate-liftbridge
./noc migrate-ch
./noc sync-perm
./noc sync-mibs
