#!./bin/python
import threading
import sys
import logging
import readline
# NOC modules
from noc.lib.nbsocket.socketfactory import SocketFactory
from noc.lib.nbsocket.pingsocket import Ping4Socket, Ping6Socket
from noc.lib.validators import is_ipv4, is_ipv6


def cb(*args):
    print "%% RESULT: %s %s" % (args[0], args[1])


def loop():
    sf = SocketFactory()
    ps4 = Ping4Socket(sf)
    ps6 = Ping6Socket(sf)
    print "Running socket factory"
    t = threading.Thread(target=sf.run)
    t.setDaemon(True)
    t.start()
    print "READY"
    while True:
        try:
            ip = raw_input("IP> ")
        except EOFError:
            print "%% STOP"
            sys.exit(0)
        ip = ip.strip()
        if not ip:
            continue
        if "*" in ip:
            ip, count = ip.split("*")
            ip = ip.strip()
            try:
                count = int(count.strip())
            except ValueError:
                print "%% ERROR: Invald count"
        else:
            count = 1
        if not is_ipv4(ip) and not is_ipv6(ip):
            print "%% ERROR: Invalid IP address"
            continue
        sock = ps6 if ":" in ip else ps4
        for i in range(count):
            sock.ping(ip, count=3, callback=cb)

if __name__ == "__main__":
    loop()
