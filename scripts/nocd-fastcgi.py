#!/usr/bin/env python
from django.core.servers.fastcgi import runfastcgi
import getopt,sys,os

SOCKET="/tmp/nocd.fcgi"
MINSPARE=2
MAXSPARE=3
MAXREQUESTS=100
MAXCHILDREN=20
PIDFILE="/var/run/nocd-fastcgi.pid"
PREFIX="/var/www/noc"

def run():
    sys.path.insert(0,PREFIX)
    prev=os.sep+os.sep.join([x for x in PREFIX.split(os.sep) if x!=""][:-1])+os.sep
    sys.path.insert(0,prev)
    os.environ['DJANGO_SETTINGS_MODULE']="noc.settings"
    runfastcgi(["method=threaded", 
                "daemonize=true",
                "socket=%s"%SOCKET,
                "minspare=%d"%MINSPARE,
                "maxspare=%d"%MAXSPARE,
                "maxrequests=%s"%MAXREQUESTS,
                "maxchildren=%s"%MAXCHILDREN,
                "pidfile=%s"%PIDFILE,
                "workdir=%s"%PREFIX])
                
def usage():
    print "USAGE:"
    print "%s [-s <socket_path>] [-S<minspare>:<maxspare>] [-C<maxchildren>] [-R<maxrequests>] [-p<pidfile>] [-r<prefix>]"%sys.argv[0]
    print "\t-s<socket_path>\t- UNIX socket for FastCGI backend"
    print "\t-S<min_spare>:<max_spare>\t- Minimum and maximum of spare threads available"
    print "\t-C<maxchildren>\t- Maximum ov threads available"
    print "\t-R<maxrequests>\t- Restart children after number of requests"
    print "\t-p<pidfile>\t- Create pid file"
    print "\t-r<prefix>\t - Root directory"
    
if __name__=="__main__":
    optlist,optarg=getopt.getopt(sys.argv[1:],"s:S:C:R:p:r:")
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
        elif k=="-r":
            PREFIX=v
        else:
            usage()
            sys.exit(1)
    run()