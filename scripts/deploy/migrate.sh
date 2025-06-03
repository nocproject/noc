#!/bin/sh
# Perform all migrations
set -e
echo "# Syncing slots"
./noc migrate-slots
echo "# Migrating"
./noc migrate
echo "# Building indexes"
./noc ensure-indexes
echo "# Syncing pools"
./noc migrate-pools
echo "# Syncing topics and partitions"
./noc migrate-liftbridge
echo "# Syncing collections"
./noc collection sync
echo "# Syncing topics and partitions (#2)"
./noc migrate-liftbridge
echo "# Syncing ClickHouse tables"
./noc migrate-ch
echo "# Syncing permissions"
./noc sync-perm
echo "# Syncing MIB"
./noc sync-mibs
