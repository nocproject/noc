#!/bin/sh
# Perform all migrations
set -e
./noc migrate
./noc sync-perm
./noc migrate-ch
./noc migrate-liftbridge
./noc collection sync
