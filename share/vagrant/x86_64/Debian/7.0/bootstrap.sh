#!/bin/sh
##----------------------------------------------------------------------
## Debian 7.0 bootstrap.sh
## Install, initialize and run NOC
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

PROGNAME=`basename $0`

error_exit ( ) {
    echo "$PROGNAME: ${1:-'Unknown error'}" 1>&2
    echo "Terminating" 1>&2
    exit 1
}

pushd /opt/noc || error_exit "No NOC distribution found"
hg in
if [ $? -eq 0 ]; then
    # Changes found
    # Fetch and restart
    hg pull -u || error_exit "Failed to fetch updates"
    popd
    exec $0
fi

# Put upgrade.conf in place
cp share/vagrant/x86_6x/Debian/7.0/files/upgrade.conf etc/upgrade.conf
# Put nginx.conf in place
cp share/vagrant/x86_6x/Debian/7.0/files/nginx.conf /etc/nginx/sites-available/noc.conf
ls -n /etc/nginx/sites-available/noc.conf /etc/nginx/sites-enabled/noc.conf
# Run NOC's upgrade process
./scripts/upgrade
