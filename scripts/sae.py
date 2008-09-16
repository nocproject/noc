#!/usr/bin/env python
#
# Service Activation Engine
#
import os,sys,getopt,logging

def usage():
    print "USAGE:"
    print "%s [-h] [-v] [-c <settings>]"%sys.argv[0]
    print "\t-h\t\t- Help screen"
    print "\t-v\t\t- Verbose debug output"

def main():
    log_level=logging.INFO
    optlist,optarg=getopt.getopt(sys.argv[1:],"vh")
    for k,v in optlist:
        if   k=="-v":
            log_level=logging.DEBUG
        elif k=="-h":
            usage()
            sys.exit(0)
    logging.basicConfig(level=log_level,format='%(asctime)s %(levelname)s %(message)s')
    logging.info("Starting LGD")
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