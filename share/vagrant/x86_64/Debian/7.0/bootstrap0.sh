#!/bin/sh
##----------------------------------------------------------------------
## Debian 7.0 bootstrap0.sh
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
    apt-get install -y $1 || error_exit "Failed to install $1"
}

##
## Update base system
##
apt-get update || die "Failed to run: apt-get: update"
apt-get upgrade || die "Failed to run: apt-get upgrade"
apt-get dist-upgrade || die "Failed to run: apt-get dist-upgrade"
##
## Create NOC user and group
##
grep -e ^noc: /etc/group
if [ $? -ne 0 ]; then
    groupadd noc
fi
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
aptinstall python
aptinstall python-dev
aptinstall python-virtualenv
aptinstall libgmp10
aptinstall libgpm-dev
aptinstall nginx
aptinstall postgresql
aptinstall postgis
aptinstall mongodb
aptinstall mercurial
##
## Set up Postgresql database
##
su - postgres << __EOF__
createuser -s -E -P noc
thenocproject
thenocproject
createdb -EUTF8 -Onoc noc
__EOF__
##
## Set up mongodb user
##
mongo noc << __EOF__
db.addUser("noc", "noc")
__EOF__
##
## Set up daemon autostart
##
update-rc.d postgresql start
update-rc.d mongodb start
update-rc.d nginx start
##
## Get NOC
##
cd /opt || error_exit "cd /opt failed"
hg clone http://hg.nocproject.org/noc noc
if [ "$1" != "--no-bootstrap" ]; then
    /opt/noc/share/vagrant/x86_64/Debian/7.0/bootstrap.sh
fi
