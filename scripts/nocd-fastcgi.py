#!/usr/bin/env python
from django.core.servers.fastcgi import runfastcgi
import getopt,sys

SOCKET="/tmp/nocd.fcgi"
MINSPARE=2
MAXSPARE=3
MAXREQUESTS=100
MAXCHILDREN=20
PIDFILE="/var/run/nocd-fastcgi.pid"

def run():
    runfastcgi(["method=threaded", 
                "daemonize=false",
                "socket=%s"%SOCKET,
                "minspare=%d"%MINSPARE,
                "maxspare=%d"%MAXSPARE,
                "maxrequests=%s"%MAXREQUESTS,
                "maxchildren=%s"%MAXCHILDREN,
                "pidfile=%s"%PIDFILE])
                
def usage():
    print "USAGE:"
    print "%s [-s <socket_path>] [-S<minspare>:<maxspare>] [-C<maxchildren>] [-R<maxrequests>] [-p<pidfile>]"%sys.argv[0]
    print "\t-s<socket_path>\t- UNIX socket for FastCGI backend"
    print "\t-S<min_spare>:<max_spare>\t- Minimum and maximum of spare threads available"
    print "\t-C<maxchildren>\t- Maximum ov threads available"
    print "\t-R<maxrequests>\t- Restart children after number of requests"
    print "\t-p<pidfile>\t- Create pid file"
    
if __name__=="__main__":
    optlist,optarg=getopt.getopt(sys.argv[1:],"s:S:C:R:p:")
    for k,v in optlist:
        if k=="-s":
            SOCKET=v
        elif k=="-S":
            MINSPARE,MAXSPARE=[int(x) for x in v.split(":")]
        elif k=="-C":
            MAXCHILDREN=int(v)
        elif k=="-R":
            MAXREQUESTS=int(v)
        elif k=="-p":
            PIDFILE=v
        else:
            usage()
            sys.exit(1)
    run()