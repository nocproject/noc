#!/bin/sh
##----------------------------------------------------------------------
## Ubuntu 12.04 bootstrap0.sh
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

aptinstall ( ) {
    info "Installing $1"
    apt-get install -y $1 || error_exit "Failed to install $1"
}
##
## Check locale settings
##
locale -a 2>&1 | grep -c locale: > /dev/null
if [ $? -eq 0 ]; then
    info "Invalid locale settings!"
    info "Please fix locale settings:"
    info "> apt-get install locales"
    info "> dpkg-reconfigure locales"
    info "Terminating"
    exit 1
fi
##
## Append additional repositories
##
apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10 || error_exit "Failed to install MongoDB Public GPG Key"
echo 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen' > /etc/apt/sources.list.d/mongodb.list
##
## Update base system
##
info "Updating base system"
apt-get update -y || error_exit "Failed to run: apt-get: update"
apt-get upgrade -y || error_exit "Failed to run: apt-get upgrade"
apt-get dist-upgrade -y || error_exit "Failed to run: apt-get dist-upgrade"
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
aptinstall less
aptinstall telnet
aptinstall tcpdump
aptinstall python
aptinstall python-dev
aptinstall python-virtualenv
aptinstall libgmp10
aptinstall libgmp-dev
aptinstall nginx
aptinstall postgresql
aptinstall libpq-dev
aptinstall mongodb-org
aptinstall mercurial
aptinstall libsmi2ldbl
aptinstall sudo
aptinstall quilt
##
## Set up Postgresql database
##
info "Create PostgreSQL 'noc' user and database"
su - postgres -c psql << __EOF__
CREATE USER noc SUPERUSER ENCRYPTED PASSWORD 'thenocproject';
CREATE DATABASE noc WITH OWNER=noc ENCODING='UTF8' TEMPLATE template0;
__EOF__
[ $? -eq 0 ] || error_exit "Failed to initialize PostgreSQL database and user"
##
## Set up mongodb user
##
info "Setting MongoDB authentication"
mongo noc << __EOF__
db.createUser({"user": "noc", "pwd": "thenocproject", "roles": ["readWrite", "dbAdmin"]})
__EOF__
##
## Set up daemon autostart
##
update-rc.d postgresql enable
update-rc.d mongodb enable
update-rc.d nginx enable
##
## Get NOC
##
cd /opt || error_exit "cd /opt failed"
if [ -z "$NOC_BRANCH" ]; then
    NOC_BRANCH=default
    export NOC_BRANCH
fi
info "Fetching NOC branch $NOC_BRANCH"
hg clone -b $NOC_BRANCH -u $NOC_BRANCH https://bitbucket.org/nocproject/noc noc || error_exit "Unable to pull NOC distribution"
if [ "$1" != "--no-bootstrap" ]; then
    info "Running bootstrap.sh"
    /opt/noc/share/vagrant/x86_64/Ubuntu/12.04/bootstrap.sh || error_exit "Failed to complete bootstrap"
    sleep 3
    echo
    info "NOC has been installed successfully"
    # Get current IP address
    IP=`ip addr show eth0 | grep "global eth0" | awk '{print $2}' | awk -F/ '{print $1}'`
    info "Follow to the NOC web interface"
    info "http://$IP/"
    info "User: admin"
    info "Password: admin"
fi
