#!/bin/sh
##----------------------------------------------------------------------
## CentOS 6.4 bootstrap0.sh
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

yuminstall ( ) {
    info "Installing $1"
    yum -y install $1 || error_exit "Failed to install $1"
}
##
## Check locale settings
##
locale -a 2>&1 | grep -c locale: > /dev/null
if [ $? -eq 0 ]; then
    info "Invalid locale settings!"
    info "Please fix locale settings:"
    info "> yum install locales"
    info "> dpkg-reconfigure locales"
    info "Terminating"
    exit 1
fi
##
## Update base system
##
info "Updating base system"
yum -y update || die "Failed to run: yum: update"
yum -y upgrade || die "Failed to run: yum upgrade"
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
## Add additional repo to yum.repos.d/CentOS-Base.repo
##
cp /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup
awk '/RPM-GPG-KEY-CentOS-6/{print;print "exclude=postgresql*";next}1' /etc/yum.repos.d/CentOS-Base.repo.backup > /etc/yum.repos.d/CentOS-Base.repo
cat >> /etc/yum.repos.d/CentOS-Base.repo << __EOF__

[mongodb]
name=MongoDB Repository
baseurl=http://downloads-distro.mongodb.org/repo/redhat/os/x86_64/
gpgcheck=0
enabled=1
__EOF__
rpm -ivh http://yum.postgresql.org/9.3/redhat/rhel-6-x86_64/pgdg-centos93-9.3-1.noarch.rpm
rpm -Uvh http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
curl -O http://yum.postgresql.org/9.3/redhat/rhel-6-x86_64/pgdg-centos93-9.3-1.noarch.rpm
##
##
## Install base packages
##
yuminstall postgresql93-server
yuminstall python-pip
yuminstall nginx
yuminstall libsmi
yuminstall mongo-10gen
yuminstall mongo-10gen-server
yuminstall openssh-clients.x86_64
yuminstall libpqxx-devel.x86_64
yuminstall python-devel.x86_64
yuminstall gmp-devel
yuminstall postgis2_93
yuminstall gcc
pip install virtualenv mercurial
##
## Init Postgresql and mongo database and daemon autostart
##
service postgresql-9.3 initdb
chkconfig postgresql-9.3 on
service postgresql-9.3 start
service mongod start
chkconfig mongod on
PATH=$PATH:/usr/pgsql-9.3/bin/
##
## Create database and user
##
info "Create PostgreSQL 'noc' user and database"
su - postgres -c psql << __EOF__
CREATE USER noc SUPERUSER ENCRYPTED PASSWORD 'thenocproject';
ALTER USER noc WITH PASSWORD 'thenocproject';
CREATE DATABASE noc WITH OWNER=noc ENCODING='UTF8';
__EOF__
[ $? -eq 0 ] || error_exit "Failed to initialize PostgreSQL database and user"
su - postgres << __EOF__
psql -f /usr/pgsql-9.3/share/contrib/postgis-2.1/postgis.sql -d noc
psql -f /usr/pgsql-9.3/share/contrib/postgis-2.1/spatial_ref_sys.sql -d noc
__EOF__
##
## Set up mongodb user
##
info "Setting MongoDB authentication"
mongo noc << __EOF__
db.addUser("noc", "thenocproject")
__EOF__
##
## IPtables service stop
##
service iptables save
service iptables stop
chkconfig iptables off
##
## Nginx daemon autostart
service nginx start
chkconfig nginx on
##
## Get NOC
##
cd /opt || error_exit "cd /opt failed"
info "Fetching NOC"
hg clone https://bitbucket.org/nocproject/noc noc || error_exit "Unable to pull NOC distribution"
virtualenv  --no-site-packages /opt/noc
if [ "$1" != "--no-bootstrap" ]; then
    info "Running bootstrap.sh"
    /opt/noc/share/vagrant/x86_64/CentOS/6.4/bootstrap.sh || error_exit "Failed to complete bootstrap"
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
