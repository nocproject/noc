##
## Various system utils
##
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
