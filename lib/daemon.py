##
## Various system utils
##
import ConfigParser,sys,logging,os

class Daemon(object):
    daemon_name="daemon"
    defaults_config_path="etc/%(daemon_name)s.defaults"
    config_path="etc/%(daemon_name)s.conf"
    
    LOG_LEVELS = {'debug'   : logging.DEBUG,
                  'info'    : logging.INFO,
                  'warning' : logging.WARNING,
                  'error'   : logging.ERROR,
                  'critical': logging.CRITICAL}
                  
    def __init__(self,config_path=None,daemonize=True):
        # Chdir to the root of project
        os.chdir(os.path.join(os.path.dirname(sys.argv[0]),".."))
        # Read config
        self.config=ConfigParser.SafeConfigParser()
        if self.defaults_config_path:
            self.config.read(self.defaults_config_path%{"daemon_name":self.daemon_name})
        if config_path:
            self.config.read(config_path)
        elif self.config_path:
            self.config.read(self.config_path%{"daemon_name":self.daemon_name})
        # Set up logging
        if self.config.get("main","loglevel") not in self.LOG_LEVELS:
            raise Exception("Invalid loglevel '%s'"%self.config.get("main","loglevel"))
        loglevel=self.LOG_LEVELS[self.config.get("main","loglevel")]
        for h in logging.root.handlers:
            logging.root.removeHandler(h) # Dirty hack for baseConfig
        if daemonize:
            if self.config.get("main","logfile"):
                logging.basicConfig(level=loglevel,
                                filename=self.config.get("main","logfile"),
                                format='%(asctime)s %(levelname)s %(message)s',
                                filemode="a+")
        else:
            logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')
        # Daemonize
        if daemonize:
            self.become_daemon() 
    ##
    ## Main daemon loop. Should be overriden
    ##
    def run(self):
        pass

    def become_daemon(self):
        try:
            if os.fork():
                sys.exit(0)
        except OSError,e:
            sys.stderr.write("Fork failed")
            sys.exit(1)
        os.setsid()
        os.umask(022)
        try:
            pid=os.fork()
        except OSError,e:
            sys.stderr.write("Fork failed")
            os._exit(1)
        if pid:
            pidfile=self.config.get("main","pidfile")
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
