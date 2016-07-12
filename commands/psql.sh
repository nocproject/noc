#!/bin/sh
# env file deployed by tower and contain following environment variables
# PGPASSFILE=var/etc/postgres/.pgpass
# PGDATABASE, PGHOST, PGPORT, PGUSER
source var/etc/postgres/env
su - $NOC_USER -c psql
