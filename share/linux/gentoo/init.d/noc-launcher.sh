#!/sbin/runscript
# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: 
DAEMON=noc-launcher

depend() {
	use net dns logger
	after postgresql-9.0
	before apache2
}

checkconfig() {
	if [ ! -f /opt/noc/etc/noc.conf ] ; then
		eerror "Please create /opt/noc/etc/noc.conf"
		eerror "Sample conf: /opt/noc/etc/noc.conf"
		return 1
	fi
	return 0
}

start() {
	checkconfig || return $?

	ebegin "Starting $DAEMON"
#	start-stop-daemon --start --chdir /opt/noc/ --exec /opt/noc/scripts/noc-launcher.py start
	cd /opt/noc
	./scripts/noc-launcher.py start
	eend $? "Failed to start $DAEMON"
}

stop() {
	ebegin "Stopping $DAEMON"
#	start-stop-daemon --stop --chdir /opt/noc/ --exec /opt/noc/scripts/noc-launcher.py stop
	cd /opt/noc
	./scripts/noc-launcher.py stop
	eend $? "Failed to stop $DAEMON"
}
