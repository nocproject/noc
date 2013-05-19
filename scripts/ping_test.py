#!./bin/python
import threading
import sys
import readline
# NOC modules
from noc.lib.nbsocket.socketfactory import SocketFactory
from noc.lib.nbsocket.pingsocket import Ping4Socket
from noc.lib.validators import is_ipv4


def cb(*args):
    print "%% RESULT: %s %s" % (args[0], args[1])


def loop():
    sf = SocketFactory()
    ps = Ping4Socket(sf)
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
        if not is_ipv4(ip):
            print "%% ERROR: Invalid IPv4"
            continue
        ps.ping(ip, count=3, callback=cb)

if __name__ == "__main__":
    loop()
