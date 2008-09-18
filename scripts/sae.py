#!/usr/bin/env python
#
# Service Activation Engine
#
import os,sys,getopt,logging

def usage():
    print "USAGE:"
    print "%s [-h] [-v] [-f] [-l<logfile>] [-p<pidfile>]"%sys.argv[0]
    print "\t-h\t\t- Help screen"
    print "\t-v\t\t- Verbose debug output"
    print "\t-f\t\t- Do not daemonize, run at the foreground"
    print "\t-l<logfile>\t- Write log to <logfile>"
    print "\t-p<pidfile>\t- Write pid to <pidfile>"
    
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
#
def main():
    log_level=logging.INFO
    run_foreground=False
    logfile=None
    pidfile=None
    optlist,optarg=getopt.getopt(sys.argv[1:],"vhfl:p:")
    for k,v in optlist:
        if   k=="-v":
            log_level=logging.DEBUG
        elif k=="-h":
            usage()
            sys.exit(0)
        elif k=="-f":
            run_foreground=True
        elif k=="-l":
            logfile=v
        elif k=="-p":
            pidfile=v
    if logfile:
        logging.basicConfig(level=log_level,filename=logfile,format='%(asctime)s %(levelname)s %(message)s',filemode="a+")
    else:
        logging.basicConfig(level=log_level,format='%(asctime)s %(levelname)s %(message)s')
    logging.info("Starting LGD")
    if not run_foreground:
        dirname=os.path.join(os.path.dirname(sys.argv[0]),"..")
        become_daemon(dirname,pidfile)
    from noc.sa.supervisor import Supervisor    
    supervisor=Supervisor()
    supervisor.run()
    
if __name__ == '__main__':
    d=os.path.dirname(sys.argv[0])
    sys.path.insert(0,os.path.join(d,"..",".."))
    sys.path.insert(0,os.path.join(d,".."))
    sys.path.insert(0,d)
    try:
        import settings
    except ImportError:
        sys.stderr.write("Error: Can't find file 'settings.py'. (If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n")
        sys.exit(1)
    main()