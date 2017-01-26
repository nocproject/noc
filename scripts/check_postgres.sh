#!/bin/sh
source var/etc/postgres/env
su - $NOC_USER -c 'psql -c "select 1"' > /dev/null 2>&1
