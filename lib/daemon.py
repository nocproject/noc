# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various system utils
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import ConfigParser,sys,logging,os,signal,optparse,datetime,traceback
from noc.lib.debug import error_report,frame_report,set_crashinfo_context,GCStats
from noc.lib.validators import is_ipv4

# Load netifaces to resolve interface addresses when possible
try:
    import netifaces
    USE_NETIFACES=True
except ImportError:
    USE_NETIFACES=False

class Daemon(object):
    daemon_name="daemon"
    defaults_config_path="etc/%(daemon_name)s.defaults"
    config_path="etc/%(daemon_name)s.conf"
    
    LOG_LEVELS = {'debug'   : logging.DEBUG,
                  'info'    : logging.INFO,
                  'warning' : logging.WARNING,
                  'error'   : logging.ERROR,
                  'critical': logging.CRITICAL}
                  
    def __init__(self):
        # Chdir to the root of project
        os.chdir(os.path.join(os.path.dirname(sys.argv[0]),".."))
        # Parse commandline
        self.opt_parser=optparse.OptionParser()
        self.opt_parser.add_option("-c","--config",action="store",type="string",dest="config",
                help="Read config from CONFIG")
        self.opt_parser.add_option("-f","--foreground",action="store_false",dest="daemonize",default=True,
                help="Do not daemonize. Run at the foreground")
        self.setup_opt_parser()
        self.options,self.args=self.opt_parser.parse_args()
        if len(self.args)<1 or self.args[0] not in ["start","stop","refresh"]:
            self.opt_parser.error("You must supply one of start|stop|refresh commands")
        # Read config
        self.config=None
        self.load_config()
        # Set up logging
        if self.config.get("main","loglevel") not in self.LOG_LEVELS:
            raise Exception("Invalid loglevel '%s'"%self.config.get("main","loglevel"))
        loglevel=self.LOG_LEVELS[self.config.get("main","loglevel")]
        for h in logging.root.handlers:
            logging.root.removeHandler(h) # Dirty hack for baseConfig
        if self.options.daemonize:
            if self.config.get("main","logfile"):
                logging.basicConfig(level=loglevel,
                                filename=self.config.get("main","logfile"),
                                format='%(asctime)s %(levelname)s %(message)s',
                                filemode="a+")
        else:
            logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')
        # GC statistics collector
        self.gc_stats=GCStats()
        # Register signal handlers if any
        for s in [s for s in dir(self) if s.startswith("SIG")]:
            try:
                sig=getattr(signal,s)
            except AttributeError:
                logging.error("Signal '%s' is not supported on this platform"%s)
                continue
            signal.signal(sig,getattr(self,s))
    ##
    ##
    ##
    def load_config(self):
        first_run=True
        if self.config:
            logging.info("Loading config")
            first_run=False
        self.config=ConfigParser.SafeConfigParser()
        if self.defaults_config_path:
            self.config.read(self.defaults_config_path%{"daemon_name":self.daemon_name})
        if self.options.config:
            self.config.read(self.options.config)
        elif self.config_path:
            self.config.read(self.config_path%{"daemon_name":self.daemon_name})
        if not first_run:
            self.on_load_config()
        if self.config.get("main","logfile"):
            set_crashinfo_context(self.daemon_name,os.path.dirname(self.config.get("main","logfile")))
        else:
            set_crashinfo_context(None,None)
    ##
    ## Called after config reloaded by SIGHUP.
    ##
    def on_load_config(self):
        pass
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
    ##
    ## Returns IP address for IP addresses or interface names
    ##
    def resolve_address(self,s):
        if is_ipv4(s):
            return s
        if USE_NETIFACES:
            try:
                a=netifaces.ifaddresses(s)
            except ValueError:
                raise Exception("Invalid interface '%s'"%s)
            try:
                return a[2][0]["addr"]
            except (IndexError,KeyError):
                raise Exception("No ip address for interface: '%s' found"%s)
        raise Exception("Cannot resolve address '%s'"%s)
    ##
    ## Add additional options to setup_opt_parser
    ##
    def setup_opt_parser(self):
        pass
    ##
    ## Process self.args[0] command
    ##
    def process_command(self):
        getattr(self,self.args[0])()
    ##
    ## "start" command handler
    ##
    def start(self):
        # Daemonize
        if self.options.daemonize:
            self.become_daemon()
        try:
            self.run()
        except KeyboardInterrupt:
            pass
        except:
            error_report()
    ##
    ## "stop" command handler
    ##
    def stop(self):
        pidfile=self.config.get("main","pidfile")
        if os.path.exists(pidfile):
            f=open(pidfile)
            pid=int(f.read().strip())
            f.close()
            logging.info("Stopping %s pid=%s"%(self.daemon_name,pid))
            try:
                os.kill(pid,signal.SIGKILL)
            except:
                pass
            os.unlink(pidfile)
    ##
    ## "refresh" command handler
    ##
    def refresh(self):
        self.stop()
        self.start()
    ##
    ## Dump current execution frame trace on SIGUSR2
    ##
    def SIGUSR2(self,signo,frame):
        frame_report(frame)
    ##
    ## Reload config on SIGHUP
    ##
    def SIGHUP(self,signo,frame):
        self.load_config()
    ##
    ## Build GC statistics on SIGPROF
    ##
    def SIGPROF(self,signo,frame):
        logging.info(self.gc_stats.report())
