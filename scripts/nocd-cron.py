#!/usr/bin/env python
import getopt,logging,sys,os

def become_daemon(dirname,pidfile=None,umask=022):
    logging.debug("Change directory to '%s'"%dirname)
    os.chdir(dirname)
    try:
        if os.fork():
            sys.exit(0)
    except OSError,e:
        sys.stderr.write("Fork failed")
        sys.exit(1)
    os.setsid()
    os.umask(umask)
    try:
        pid=os.fork()
    except OSError,e:
        sys.stderr.write("Fork failed")
        os._exit(1)
    if pid:
        if pidfile:
            f=open(pidfile,"w")
            f.write(str(pid))
            f.close()
        os._exit(0)
    i=open("/dev/null","r")
    o=open("/dev/null","a+")
    e=open("/dev/null","a+")
    os.dup2(i.fileno(), sys.stdin.fileno())
    os.dup2(o.fileno(), sys.stdout.fileno())
    os.dup2(e.fileno(), sys.stderr.fileno())
    sys.stdout=o
    sys.stderr=e
    
def usage():
    print "USAGE:"
    print "%s [-h] [-v] [-f] [-p<pidfile>] [-l<logfile>]"%sys.argv[0]
    print "\t-h\t\t- This screen"
    print "\t-v\t\t- Verbose logging"
    print "\t-f\t\t- Do not daemonize, run at the foreground"
    print "\t-p<pidfile>\t- Write pidfile at the <pidfile>"
    print "\t-l<logfile>\t- Write log file"
    

if __name__=="__main__":
    d=os.path.dirname(sys.argv[0])
    sys.path.insert(0,os.path.join(d,"..",".."))
    sys.path.insert(0,os.path.join(d,".."))
    sys.path.insert(0,d)
    log_level=logging.INFO
    daemonize=True
    logfile=None
    pidfile=None
    optlist,optarg=getopt.getopt(sys.argv[1:],"vhfp:l:")
    for k,v in optlist:
        if k=="-v":
            log_level=logging.DEBUG
        elif k=="-f":
            daemonize=False
        elif k=="-h":
            usage()
        elif k=="-p":
            pidfile=v
        elif k=="-l":
            logfile=l
    if logfile:
        logging.basicConfig(level=log_level,filename=logfile,format='%(asctime)s %(levelname)s %(message)s',filemode="a+")
    else:
        logging.basicConfig(level=log_level,format='%(asctime)s %(levelname)s %(message)s')
    logging.info("Starting CRON")
    if daemonize:
        dirname=os.path.join(os.path.dirname(sys.argv[0]),"..")
        become_daemon(dirname,pidfile)
    os.environ['DJANGO_SETTINGS_MODULE']="noc.settings"
    from noc.main.cron import CronDaemon
    cd=CronDaemon()
    cd.run()