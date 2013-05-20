#!/bin/sh
##----------------------------------------------------------------------
## Debian 7.0 bootstrap.sh
## Install, initialize and run NOC
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

PROGNAME=`basename $0`
DIST=/opt/noc/share/vagrant/x86_64/Debian/7.0

error_exit ( ) {
    echo "$PROGNAME: ${1:-'Unknown error'}" 1>&2
    echo "Terminating" 1>&2
    exit 1
}

START_DIR=$PWD
cd /opt/noc || error_exit "No NOC distribution found"
hg in
if [ $? -eq 0 ]; then
    # Changes found
    # Fetch and restart
    hg pull -u || error_exit "Failed to fetch updates"
    cd $START_DIR
    exec $0
fi

# Put upgrade.conf in place
cp $DIST/files/upgrade.conf etc/upgrade.conf || error_exit "Cannot copy upgrade.conf"
# Put nginx.conf in place
rm -f /etc/nginx/sites-enabled/default
cp $DIST/files/nginx.conf /etc/nginx/sites-available/noc.conf || error_exit "Cannot copy nginx config"
ln -s /etc/nginx/sites-available/noc.conf /etc/nginx/sites-enabled/noc.conf || error_exit "Cannot set up nginx config"
# Put init script
cp $DIST/files/noc-launcher /etc/init.d/ || error_exit "Cannot install init file"
update-rc.d noc-launcher start
# Run NOC's upgrade process
./scripts/upgrade
