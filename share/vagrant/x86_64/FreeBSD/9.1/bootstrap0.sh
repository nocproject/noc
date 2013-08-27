#!/bin/sh
##----------------------------------------------------------------------
## FreeBSD 9.1 bootstrap0.sh
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

install_port ( ) {
    info "Installing $1"
    cd /usr/ports/$1 || error_exit "Port not found: $1"
    make || error_exit "Failed to make port: $1"
    make install || error_exit "Failed to install port: $1"
    make clean || error_exit "Failed to clean port: $1"
}

##
## Create NOC user and group
##
info "Create group 'noc'"
grep -e ^noc: /etc/group
if [ $? -ne 0 ]; then
    pw groupadd -n noc
fi
info "Create user 'noc'"
grep -e ^noc: /etc/passwd
if [ $? -ne 0 ]; then
    pw useradd -g noc -s /bin/sh -d /home/noc -n noc
    passwd noc << __EOF__
thenocproject
thenocproject
__EOF__
fi
##
## Install base packages
##
info "Installing system packages"
install_port databases/postgresql93-server
install_port databases/postgis20
install_port databases/mongodb
install_port devel/py-virtualenv
install_port net-mgmt/libsmi
install_port www/nginx
install_port devel/mercurial
##
## Set up Postgresql database
##
info "Create PostgreSQL 'noc' user and database"
mkdir /var/db/pgsql || error_exit "Cannot create /var/db/pgsql"
mkdir /var/db/pgsql/data || error_exit "Cannot create /var/db/pgsql/data"
chown -R pgsql:pgsql /var/db/pgsql/ || error_exit "Cannot set user on /var/db/pgsql"
chmod -R 750 /var/db/pgsql/ || error_exit "Cannot set permissions on /var/db/pgsql"
/usr/local/etc/rc.d/postgresql initdb || error_exit "Cannot initialize PostgreSQL database"
/usr/local/etc/rc.d/postgresql start || error_exit "Cannot start PostgreSQL database"
su - pgsql -c psql << __EOF__
CREATE USER noc SUPERUSER ENCRYPTED PASSWORD 'thenocproject';
CREATE DATABASE noc WITH OWNER=noc ENCODING='UTF8';
__EOF__
[ $? -eq 0 ] || error_exit "Failed to initialize PostgreSQL database and user"
##
## Set up mongodb user
##
info "Launching MongoDB database"
/usr/local/etc/rc.d/mongod start || error_exit "Cannot start MongoDB database"
info "Setting MongoDB authentication"
mongo noc << __EOF__
db.addUser("noc", "thenocproject")
__EOF__
##
## Set up daemon autostart
##
echo "postgresql_enable="YES"" >> /etc/rc.conf
echo "postgresql_data="/var/db/pgsql/data"" >> /etc/rc.conf
echo "mongod_enable="YES"" >> /etc/rc.conf
echo "mongod_dbpath="/var/db/mongo"" >> /etc/rc.conf
##
## Get NOC
##
cd /opt || error_exit "cd /opt failed"
info "Fetching NOC"
hg clone https://bitbucket.org/nocproject/noc noc || error_exit "Unable to pull NOC distribution"
if [ "$1" != "--no-bootstrap" ]; then
    info "Running bootstrap.sh"
    /opt/noc/share/vagrant/x86_64/FreeBSD/9.1/bootstrap.sh
fi
