#!/usr/bin/env python
#
# Service Activation Engine
#
import os,sys,getopt,logging

def usage():
    print "USAGE:"
    print "%s [-h] [-v] [-f] [-L<ip>:<port>] [-l<logfile>] [-p<pidfile>]"%sys.argv[0]
    print "\t-h\t\t- Help screen"
    print "\t-v\t\t- Verbose debug output"
    print "\t-f\t\t- Do not daemonize, run at the foreground"
    print "\t-L\t\t- Listen at <ip>:<port>"
    print "\t-l<logfile>\t- Write log to <logfile>"
    print "\t-p<pidfile>\t- Write pid to <pidfile>"
#
def main():
    log_level=logging.INFO
    run_foreground=False
    ip="127.0.0.1"
    port=19701
    logfile=None
    pidfile=None
    optlist,optarg=getopt.getopt(sys.argv[1:],"vhfl:p:L:")
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
        elif k=="-L":
            ip,port=v.split(":")
            port=int(port)
    if logfile:
        logging.basicConfig(level=log_level,filename=logfile,format='%(asctime)s %(levelname)s %(message)s',filemode="a+")
    else:
        logging.basicConfig(level=log_level,format='%(asctime)s %(levelname)s %(message)s')
    logging.info("Starting SAE")
    if not run_foreground:
        from noc.lib.sysutils import become_daemon
        dirname=os.path.join(os.path.dirname(sys.argv[0]),"..")
        become_daemon(dirname,pidfile)
    os.environ['DJANGO_SETTINGS_MODULE']="noc.settings"
    from noc.sa.sae import SAE
    sae=SAE(ip,port)
    sae.run()
    
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