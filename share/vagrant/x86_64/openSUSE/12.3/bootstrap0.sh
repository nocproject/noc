#!/bin/sh
##----------------------------------------------------------------------
## openSUSE 12.3 bootstrap0.sh
## Initialize system and install all prerequisites to NOC
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

##
## Helper functions definitions
##
PROGNAME=`basename $0`

error_exit ( ) {
    echo "$PROGNAME: ${1:-'Unknown error'}" 1>&2
    echo "Terminating" 1>&2
    exit 1
}

info ( ) {
    echo $1 1>&2
}

zinstall ( ) {
    info "Installing $1"
    zypper --non-interactive install -y $1 || error_exit "Failed to install $1"
}

##
## Update base system
##
info "Updating base system"
# Disable cdrom-based repo
zypper mr -d 1 || error_exit "Unable to disable CDROM repo"
# Install patches
zypper --non-interactive patch || error_exit "Unable to patch"

##
## Create NOC user and group
##
info "Create group 'noc'"
grep -e ^noc: /etc/group
if [ $? -ne 0 ]; then
    groupadd noc
fi
info "Create user 'noc'"
grep -e ^noc: /etc/passwd
if [ $? -ne 0 ]; then
    useradd -g noc -s /bin/bash -d /home/noc -m noc
    passwd noc << __EOF__
thenocproject
thenocproject
__EOF__
fi
##
## Install base packages
##

# Attach repos
zypper ar -G http://download.opensuse.org/repositories/server:/database/openSUSE_12.3 server:database || error_exit "Unable to add repo server:database"
zypper ar -G http://download.opensuse.org/repositories/Application:/Geo/openSUSE_12.3 Application:Geo || error_exit "Unable to add repo Application:Geo"
# Install packages
zypper --non-interactive remove patterns-openSUSE-minimal_base-conflicts
zinstall tcpdump
zinstall python-devel
zinstall libgmp10
zinstall gmp-devel
zinstall libsmi
zinstall postgresql
zinstall nginx
zinstall python-pip
zinstall python-virtualenv
zinstall mercurial
zinstall mongodb
zinstall postgis2
##
## Set up Postgresql database
##
info "Create PostgreSQL 'noc' user and database"
/etc/init.d/postgresql start
su - postgres -c psql << __EOF__
CREATE USER noc SUPERUSER ENCRYPTED PASSWORD 'thenocproject';
CREATE DATABASE noc WITH OWNER=noc ENCODING='UTF8';
__EOF__
[ $? -eq 0 ] || error_exit "Failed to initialize PostgreSQL database and user"
##
## Set up mongodb user
##
info "Setting MongoDB authentication"
/etc/init.d/mongodb start
mongo noc << __EOF__
db.addUser("noc", "thenocproject")
__EOF__
##
## Set up daemon autostart
##
chkconfig nginx on
chkconfig postgresql on
chkconfig mongodb on
##
## Get NOC
##
cd /opt || error_exit "cd /opt failed"
info "Fetching NOC"
hg clone http://hg.nocproject.org/noc noc
if [ "$1" != "--no-bootstrap" ]; then
    info "Running bootstrap.sh"
    /opt/noc/share/vagrant/x86_64/openSUSE/12.3/bootstrap.sh
fi
