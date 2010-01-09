# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## noc-launcher daemon
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.lib.daemon import Daemon
from noc.lib.debug import DEBUG_CTX_CRASH_PREFIX
import time,subprocess,sys,os,logging,stat,ConfigParser,pwd,grp,atexit,signal,stat
##
HEARTBEAT_TIMEOUT=10
##
## Daemon wrapper
##
class DaemonData(object):
    def __init__(self,name,is_superuser,enabled,user,uid,group,gid):
        logging.debug("Reading config for %s"%name)
        self.config=ConfigParser.SafeConfigParser()
        self.config.read("etc/%s.defaults"%name)
        self.config.read("etc/%s.conf"%name)
        self.name=name
        self.enabled=enabled
        self.pid=None
        self.pidfile=self.config.get("main","pidfile")
        self.is_superuser=is_superuser
        self.user=user
        self.uid=uid
        self.group=group
        self.gid=gid
        self.enable_heartbeat=self.config.getboolean("main","heartbeat")
        self.next_heartbeat_check=0
    
    def __repr__(self):
        return "<DaemonData %s>"%self.name
    ##
    ## Launch daemon
    ##
    def launch(self):
        logging.info("Launching %s"%self.name)
        try:
            pid=os.fork()
        except OSError, e:
            logging.error("%s: Fork failed: %s(%s)"%(self.name,e.strerror,e.errno))
            return
        if pid:
            self.pid=pid
            logging.info("Daemon %s started as PID %d"%(self.name,self.pid))
            self.next_heartbeat_check=time.time()+HEARTBEAT_TIMEOUT
        else:
            # Run child
            try:
                if self.group:
                    os.setgid(self.gid)
                    os.setegid(self.gid)
                if self.user:
                    os.setuid(self.uid)
                    os.seteuid(self.uid)
                    # Set up EGG Cache to prevent permissions problem in python 2.6
                    os.environ["PYTHON_EGG_CACHE"]="/tmp/.egg-cache%d"%self.uid
                os.execv(sys.executable,[sys.executable,"./scripts/%s.py"%self.name,"launch"])
            except OSError, e:
                logging.error("%s: OS Error: %s(%s)"%(self.name,e.strerror,e.errno))
                sys.exit(1)
    ##
    ## Kill daemon
    ##
    def kill(self):
        if not self.pid:
            logging.info("%s: No PID to kill"%self.name)
        try:
            logging.info("%s: killing"%self.name)
            os.kill(self.pid,signal.SIGTERM)
        except:
            logging.error("%s: Unable to kill daemon"%self.name)
    ##
    ##
    ##
    def check_heartbeat(self):
        if not self.enabled or not self.pid or not self.enable_heartbeat:
            return
        t=time.time()
        if t<self.next_heartbeat_check:
            return
        logging.debug("Checking heartbeat from %s"%self.name)
        self.next_heartbeat_check=t+HEARTBEAT_TIMEOUT
        try:
            mt=os.stat(self.pidfile)[stat.ST_MTIME]
        except:
            logging.error("Unable to stat pidfile: %s"%self.pidfile)
            return
        if t-mt>=HEARTBEAT_TIMEOUT:
            logging.info("%s: Heartbeat lost. Restarting"%self.name)
            self.kill()

class Launcher(Daemon):
    daemon_name="noc-launcher"
    def __init__(self):
        super(Launcher,self).__init__()
        self.daemons=[]
        gids={}
        uids={}
        self.is_superuser=os.getuid()==0
        self.crashinfo_uid=None
        self.crashinfo_dir=None
        for n in ["fcgi","sae","activator","classifier","correlator","notifier","probe"]:
            dn="noc-%s"%n
            is_enabled=self.config.getboolean(dn,"enabled")
            # Resolve group name
            group_name=self.config.get(dn,"group")
            if group_name:
                if group_name not in gids:
                    try:
                        gid=grp.getgrnam(group_name)[2]
                        gids[group_name]=gid
                    except KeyError:
                        logging.error("Group '%s' is not found. Exiting."%group_name)
                        sys.exit(1)
                gid=gids[group_name]
            else:
                gid=None
            # Resolve user name
            user_name=self.config.get(dn,"user")
            if user_name:
                if user_name not in uids:
                    try:
                        uid=pwd.getpwnam(user_name)[2]
                        uids[user_name]=uid
                    except KeyError:
                        logging.error("User '%s' is not found. Exiting."%user_name)
                        sys.exit(1)
                uid=uids[user_name]
            else:
                uid=None
            # Superuser required to change uid/gid
            if not self.is_superuser and uids:
                logging.error("Need to be superuser to change UID")
                sys.exit(1)
            if not self.is_superuser and gids:
                logging.error("Need to be superuser to change GID")
                sys.exit(1)
            # Initialize daemon data
            self.daemons+=[
                DaemonData(dn,
                    is_superuser = self.is_superuser,
                    enabled = is_enabled,
                    user    = user_name,
                    uid     = uid,
                    group   = group_name,
                    gid     = gid)
                    ]
            # Set crashinfo uid
            if self.is_superuser and dn=="noc-sae" and is_enabled:
                self.crashinfo_uid=uid
                self.crashinfo_dir=os.path.dirname(self.config.get("main","logfile"))
        #
        atexit.register(self.at_exit)
    ##
    ## Build contrib/lib if necessary
    ##
    def sync_contrib(self):
        sync_dir=os.path.join(os.path.dirname(sys.argv[0]),"..","contrib","src","bin")
        if os.path.exists(os.path.join(sync_dir,"sync")):
            logging.info("Syncronizing contrib")
            wd=os.getcwd()
            os.chdir(sync_dir)
            r=subprocess.call(["./sync"])
            os.chdir(wd)
            if r==0:
                logging.info("contrib syncronized")
            else:
                logging.error("contrib syncronization failed")
        else:
            logging.info("Skipping contrib syncronization")
    ##
    ## Main Loop
    ##
    def run(self):
        self.sync_contrib()
        last_crashinfo_check=time.time()
        while True:
            for d in self.daemons:
                if not d.enabled: # Skip disabled daemons
                    continue
                if d.pid is None: # Launch required daemons
                    d.launch()
                else: # Check daemon status
                    try:
                        pid,status=os.waitpid(d.pid,os.WNOHANG)
                    except OSError:
                        pid=0
                        status=0
                    if pid==d.pid:
                        logging.info("%s daemon is terminated with status %d"%(d.name,d.pid))
                        d.pid=None
            time.sleep(1)
            t=time.time()
            if self.crashinfo_uid is not None and t-last_crashinfo_check>10:
                # Fix crashinfo's permissions
                for fn in [fn for fn in os.listdir(self.crashinfo_dir) if fn.startswith(DEBUG_CTX_CRASH_PREFIX)]:
                    path=os.path.join(self.crashinfo_dir,fn)
                    try:
                        if os.stat(path)[stat.ST_UID]==self.crashinfo_uid:
                            continue # No need to fix
                    except OSError:
                        continue # stat() failed
                    try:
                        os.chown(path,self.crashinfo_uid,-1)
                        os.chmod(path,stat.S_IRUSR|stat.S_IWUSR)
                        logging.info("Permissions for %s are fixed"%path)
                    except:
                        logging.error("Failed to fix permissions for %s"%path)
                last_crashinfo_check=t
            # Check heartbeats
            [d for d in self.daemons if d.check_heartbeat()]
        
    def at_exit(self):
        for d in self.daemons:
            if d.enabled and d.pid:
                try:
                    logging.info("Stopping daemon: %s (PID %d)"%(d.name,d.pid))
                    os.kill(d.pid,signal.SIGKILL)
                    d.pid=None
                except OSError:
                    pass
        logging.info("STOP")
    
    def SIGTERM(self,signo,frame):
        self.at_exit()
        os._exit(0)
