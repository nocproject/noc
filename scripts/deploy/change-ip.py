#!./bin/python
# ----------------------------------------------------------------------
# Change NOC's ip address
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import sys
import socket
import fileinput

TOWER_DB_PATH = "/opt/tower/var/tower/db/config.db"
PG_VERSION = "9.6"
PG_DEB_PATH = "/etc/postgresql/" + PG_VERSION + "/main/noc.conf"
PG_RPM_PATH = "/var/lib/pgsql/" + PG_VERSION + "/data/noc.conf"
NATS_DEB_PATH = "/etc/nats/nats-server.conf"
LB_DEB_PATH = "/etc/liftbridge/liftbridge.yml"
NGINX_DEB_PATH = "/etc/nginx/conf.d/noc.conf"
MONGO_DEB_PATH = "/etc/mongod.conf"
CONSUL_DEB_PATH = "/etc/consul/config.json"
CONSUL_ng_path = "/etc/consul.d/nginx.json"
CONSUL_nats_path = "/etc/consul.d/nats.json"
CONSUL_lift_path = "/etc/consul.d/liftbridge.json"
CONSUL_pg_path = "/etc/consul.d/scripts/postgres_check.sh"
GRAFANA_DEB_PATH = "/etc/grafana/grafana.ini"
CLICKHOUSE_DEB_PATH = "/etc/clickhouse-server/users.xml"

ALL_PATHS = [
    PG_DEB_PATH,
    MONGO_DEB_PATH,
    NATS_DEB_PATH,
    LB_DEB_PATH,
    NGINX_DEB_PATH,
    CONSUL_DEB_PATH,
    CONSUL_ng_path,
    CONSUL_nats_path,
    CONSUL_lift_path,
    CONSUL_pg_path,
    GRAFANA_DEB_PATH,
    CLICKHOUSE_DEB_PATH,
]


def get_my_ip():
    """Find out what ip address is lead to defroute interface"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
        print("Can't find proper IP interface")
    finally:
        s.close()
    return ip


def change_ip_address(path, old_ip, new_ip):
    try:
        if os.path.isfile(path):
            print("Changing ip in: ", path)
            for line in fileinput.input(files=path, inplace=True):
                line = line.replace(old_ip, new_ip)
                sys.stdout.write(line)
            print("OK")
    except IOError:
        pass


def get_old_ip():
    """Read old ip from file from /etc/hosts"""
    try:
        ipfilepath = "/etc/hosts"
        with open(ipfilepath, "r") as file:
            hostname = socket.gethostname()
            for line in file.readlines():
                if line.strip().endswith(hostname):
                    old_address = line.split()[0]
                    return old_address
    except EnvironmentError:
        print("No file with old IP")


def set_hosts_address(address):
    """Set new IP to /etc/hosts"""
    deb_path = "/etc/hosts"
    for path in [deb_path]:
        try:
            if os.path.isfile(path):
                hostname = socket.gethostname()
                for line in fileinput.input(files=path, inplace=True):
                    if line.strip().endswith(hostname):
                        line = address + " " + hostname + "\n"
                    sys.stdout.write(line)
            return
        except IOError:
            pass
    print("You haven't /etc/hosts")


def change_ip_everywhere(paths, old_ip, new_ip):
    """Change ip in every known path"""
    for path in paths:
        change_ip_address(path, old_ip, new_ip)
    print("Done changing")


def change_inside_tower(old_ip, new_ip):
    """Change ip inside tower.db on same host"""
    try:
        if os.path.isfile(TOWER_DB_PATH):
            print("Changing address in: ", TOWER_DB_PATH)
            os.system(f"sqlite3 {TOWER_DB_PATH} \"UPDATE node SET address = '{new_ip}';\"")
            os.system(
                f"sqlite3 {TOWER_DB_PATH} \"UPDATE environment SET web_host = '{new_ip}' where web_host = '{old_ip}';\""
            )
    except IOError:
        pass


if __name__ == "__main__":
    old_ip_address = get_old_ip()
    print("Old ip was: ", old_ip_address)

    my_ip = get_my_ip()
    print("Local ip is: ", my_ip)

    set_hosts_address(my_ip)
    change_ip_everywhere(ALL_PATHS, old_ip_address, my_ip)

    print("Restarting services")
    os.system(f"chown nats {NATS_DEB_PATH}")
    os.system("systemctl restart nats-server")
    os.system("systemctl restart liftbridge")
    os.system("systemctl restart postgresql")
    os.system("systemctl restart consul")
    os.system("systemctl restart mongod")

    os.system("systemctl restart noc")
    change_inside_tower(old_ip_address, my_ip)
    print("That's all")
