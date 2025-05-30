#!/bin/sh
# Perform all migrations
set -e
./noc migrate-slots
./noc migrate
./noc ensure-indexes
./noc migrate-pools
./noc migrate-liftbridge
./noc collection sync
./noc migrate-liftbridge
./noc migrate-ch
./noc sync-perm
./noc sync-mibs
