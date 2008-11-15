#!/usr/bin/env python
#
# Service Activation Engine
#
import os,sys,getopt,logging

def usage():
    print "USAGE:"
    print "%s [-h] [-v] [-f] [-n<name>][-c<ip>:<port>] [-l<logfile>] [-p<pidfile>] [-t<ip>]"%sys.argv[0]
    print "\t-h\t\t- Help screen"
    print "\t-v\t\t- Verbose debug output"
    print "\t-f\t\t- Do not daemonize, run at the foreground"
    print "\t-n<name>\t-Set instance name"
    print "\t-c\t\t- Connect to SAE at <ip>:<port>"
    print "\t-l<logfile>\t- Write log to <logfile>"
    print "\t-p<pidfile>\t- Write pid to <pidfile>"
    print "\t-t<ip>\t- Listen for SNMP traps at <ip>"
#
def main():
    log_level=logging.INFO
    run_foreground=False
    ip="127.0.0.1"
    port=19701
    logfile=None
    pidfile=None
    name="unknown"
    trap_ip=None
    optlist,optarg=getopt.getopt(sys.argv[1:],"vhfl:p:c:n:t:")
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
        elif k=="-c":
            ip,port=v.split(":")
            port=int(port)
        elif k=="-n":
            name=v
        elif k=="-t":
            trap_ip=v
    if logfile:
        logging.basicConfig(level=log_level,filename=logfile,format='%(asctime)s %(levelname)s %(message)s',filemode="a+")
    else:
        logging.basicConfig(level=log_level,format='%(asctime)s %(levelname)s %(message)s')
    logging.info("Starting Activator")
    if not run_foreground:
        from noc.lib.sysutils import become_daemon
        dirname=os.path.join(os.path.dirname(sys.argv[0]),"..")
        become_daemon(dirname,pidfile)
    software_update=not os.path.exists(os.path.join("sa","sae.py"))
    from noc.sa.activator import Activator
    activator=Activator(name,ip,port,trap_ip,software_update)
    activator.run()
    
if __name__ == '__main__':
    d=os.path.dirname(sys.argv[0])
    sys.path.insert(0,os.path.join(d,"..",".."))
    sys.path.insert(0,os.path.join(d,".."))
    sys.path.insert(0,d)
    main()