# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various system utils
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import ConfigParser,sys,logging,os,signal,optparse,datetime,traceback
import logging.handlers
from noc.lib.debug import error_report,frame_report,set_crashinfo_context,GCStats
from noc.lib.validators import is_ipv4, is_int
from noc.lib.version import get_version

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
        self.opt_parser.add_option("-V","--version",action="store_true",dest="show_version",default=False,
                help="Show daemon version")
        self.setup_opt_parser()
        self.options,self.args=self.opt_parser.parse_args()
        if self.options.show_version:
            print get_version()
            sys.exit(0)
        if len(self.args)<1 or self.args[0] not in ["start","launch","stop","refresh"]:
            self.opt_parser.error("You must supply one of start|launch|stop|refresh commands")
        # Read config
        self.pidfile=None
        self.config=None
        self.load_config()
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
        # Set up logging
        if self.config.get("main","loglevel") not in self.LOG_LEVELS:
            raise Exception("Invalid loglevel '%s'"%self.config.get("main","loglevel"))
        for h in logging.root.handlers:
            logging.root.removeHandler(h) # Dirty hack for baseConfig
        self.heartbeat_enable=self.options.daemonize and self.config.getboolean("main","heartbeat")
        if self.options.daemonize:
            if self.config.get("main","logfile"):
                loglevel=self.LOG_LEVELS[self.config.get("main","loglevel")]
                logging.root.setLevel(loglevel)
                rf_handler=logging.handlers.RotatingFileHandler(
                    filename=self.config.get("main","logfile"),
                    maxBytes=self.config.getint("main","logsize"),
                    backupCount=self.config.getint("main","logfiles")
                )
                rf_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s',None))
                logging.root.addHandler(rf_handler)
            self.pidfile=self.config.get("main","pidfile")
        else:
            logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')
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
                # Exit parent and retur control to the shell immediately
                sys.exit(0)
        except OSError,e:
            sys.stderr.write("Fork failed")
            sys.exit(1)
        os.setsid() # Become session leader
        os.umask(022)
        try:
            pid=os.fork()
        except OSError,e:
            sys.stderr.write("Fork failed")
            os._exit(1)
        if pid:
            if self.pidfile:
                f=open(self.pidfile,"w")
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
    ## Parses string and returns a list of (ip,port)
    ## Addresses are separated by comma
    ## Possible entries:
    ## * ip
    ## * ip:port
    ## * iface
    ## * iface:port
    ##
    def resolve_addresses(self,addr_list,default_port):
        r=[]
        for x in addr_list.split(","):
            x=x.strip()
            if not x:
                continue
            if ":" in x: # Implicit port notation
                x,port=x.split(":",1)
                if is_int(port):
                    port=int(port)
                else:
                    try:
                        port=socket.getservbyname(port)
                    except socket.error:
                        raise Exception("Invalid port: %s"%port)
            else:
                port=int(default_port)
            if port<=0 or port>65535:
                raise Exception("Invalid port: %s"%port)
            if is_ipv4(x):
                r+=[(x,port)]
                continue
            if USE_NETIFACES: # Can resolve interface names
                try:
                    a=netifaces.ifaddresses(x)
                except ValueError:
                    raise Exception("Invalid interface '%s'"%x)
                try:
                    x=a[2][0]["addr"]
                except (IndexError,KeyError):
                    raise Exception("No ip address for interface: '%s' found"%x)
                r+=[(x,port)]
                continue
            raise Exception("Cannot resolve address '%s'"%x)
        return r
    ##
    ## Touch pidfile
    ##
    def heartbeat(self):
        if self.pidfile and self.heartbeat_enable:
            try:
                logging.debug("Touching pidfile: %s"%self.pidfile)
                os.utime(self.pidfile,None)
            except:
                logging.error("Unable to touch pidfile")
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
                os.kill(pid,signal.SIGTERM)
            except:
                pass
            os.unlink(pidfile)
    ##
    ## "launch" command handler
    ##
    def launch(self):
        # Write pidfile
        pid=os.getpid()
        f=open(self.pidfile,"w")
        f.write(str(pid))
        f.close()
        # Close stdin/stdout/stderr
        i=open("/dev/null","r")
        o=open("/dev/null","a+")
        e=open("/dev/null","a+")
        os.dup2(i.fileno(), sys.stdin.fileno())
        os.dup2(o.fileno(), sys.stdout.fileno())
        os.dup2(e.fileno(), sys.stderr.fileno())
        sys.stdout=o
        sys.stderr=e
        try:
            self.run()
        except KeyboardInterrupt:
            pass
        except:
            error_report()
    
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
    ##
    ##
    ##
    def SIGINT(self,signo,frame):
        logging.info("SIGINT received. Exiting")
        os._exit(0)
