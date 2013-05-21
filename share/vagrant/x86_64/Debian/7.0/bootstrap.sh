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
./scripts/upgrade || error_exit "Failed to upgrade NOC"
# Set up configs
./scripts/set-conf.py etc/noc-launcher.conf noc-activator user root
./scripts/set-conf.py etc/noc-activator.conf activator listen_traps eth0
./scripts/set-conf.py etc/noc-activator.conf activator listen_syslog eth0
./scripts/set-conf.py etc/noc-activator.conf activator name default
./scripts/set-conf.py etc/noc-activator.conf activator secret thenocproject
su - postgres -c "psql noc" << __EOF__
BEGIN;
UPDATE sa_activator SET auth='thenocproject';
COMMIT;
__EOF__
[ $? -ne 0 ] && error_exit "Failed to set activator password"
# Run nginx
/etc/init.d/nginx restart
# Run NOC
/etc/init.d/noc-launcher start
