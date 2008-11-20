##
## BaseAction implementation
## Action is a scenario executed upon stream
##
from noc.lib.ecma48 import strip_control_sequences
from noc.lib.nbsocket import ConnectedTCPSocket,PTYSocket
from noc.lib.registry import Registry
from noc.sa.protocols.sae_pb2 import TELNET,SSH,HTTP
import logging,re

##
##
##
class ActionRegistry(Registry):
    name="ActionRegistry"
    subdir="actions"
    classname="Action"
    apps=["noc.sa"]

action_registry=ActionRegistry()
##
##
##
class ActionBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        action_registry.register(m.name,m)
        return m
##
##
##
class Action(object):
    __metaclass__=ActionBase
    name=None
    ARGS=[]
    CLEAN_INPUT=False # Strip Profile.rogue_chars and ECMA-48 control sequences
    def __init__(self,transaction_id,stream,profile,callback,args=None):
        self.callback=callback
        self.transaction_id=transaction_id
        self.profile=profile
        self.stream=stream
        self.fsm=None
        self.args={}
        self.buffer=""
        self.result=""
        self.status=False
        self.to_collect_result=False
        self.to_reconnect=False
        if args:
            self.set_args(args)
        self.stream.attach_action(self)
        self.prepare_action()
    
    # Abstract method to be overriden
    def prepare_action(self):
        pass
    #
    def set_args(self,args):
        logging.debug("%s set_args %s"%(str(self),str(args)))
        for k in self.ARGS:
            self.args[k]=None
        for k,v in args.items():
            if k not in self.args:
                raise Exception,"Unknown argument: %s"%k
            self.args[k]=v
            
    def close(self,status):
        if self.to_reconnect:
            logging.debug("Reconnecting")
            self.stream.close()
            self.stream.prepare_socket()
            return
        logging.debug("%s close(%s)"%(str(self),status))
        if self.buffer:
            self.stream.retain_input(self.buffer)
        self.stream.attach_action(None)
        self.stream.close()
        self.status=status
        self.callback(self)
    
    def set_fsm(self,fsm):
        logging.debug("FSM set: %s"%str(fsm))
        if fsm:
            # Immediate success/failure
            if fsm=="SUCCESS":
                self.close(True)
                return
            if fsm=="FAILURE":
                self.close(False)
                return
            self.fsm=[]
            for stmt in fsm:
                # Install FSM
                rx=re.compile(stmt[0],re.DOTALL|re.MULTILINE)
                action=stmt[1]
                if action=="SUCCESS":
                    action=self.s_success
                elif action=="FAILURE":
                    action=self.s_failure
                self.fsm.append((rx,action))
        else:
            self.fsm=None
    ##
    ## Called by activator's stream on new data ready
    ##
    def feed(self,msg):
        logging.debug("%s feed: %s"%(str(self),repr(msg)))
        if self.CLEAN_INPUT and self.profile.rogue_chars:
            for rc in self.profile.rogue_chars:
                msg=msg.replace(rc,"")
        self.buffer+=msg
        if self.CLEAN_INPUT:
            self.buffer=strip_control_sequences(self.buffer)
            logging.debug("%s buffer after cleaning: %s"%(str(self),repr(self.buffer)))
        while self.buffer and self.fsm:
            matched=False
            for rx,action in self.fsm:
                match=rx.search(self.buffer)
                if match:
                    matched=True
                    logging.debug("FSM MATCH: %s"%rx.pattern)
                    if self.to_collect_result:
                        self.result+=self.buffer[:match.start(0)]
                    self.buffer=self.buffer[match.end(0):]
                    self.set_fsm(action(match))
                    break
            if not matched:
                break
                
    def submit(self,msg):
        logging.debug("%s submit: %s"%(str(self),msg.replace("\n","\\n")))
        self.stream.write(msg+self.profile.command_submit)
        
    def output(self,msg):
        pass
        
    def s_success(self,match):
        self.close(True)
        
    def s_failure(self,match):
        self.close(False)
##
##
##
class SchemeRegistry(Registry):
    name="SchemeRegistry"
    def __init__(self):
        Registry.__init__(self)
        self.name_to_id={}
        self.id_to_name={}

    def register(self,name,cls):
        Registry.register(self,name,cls)
        self.name_to_id[name]=cls.scheme_id
        self.id_to_name[cls.scheme_id]=name
        
    def get_by_id(self,scheme_id):
        return self[self.id_to_name[scheme_id]]

scheme_registry=SchemeRegistry()
##
##
##
class SchemeSocketBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        scheme_registry.register(m.name,m)
        return m
##
## Socket mixin
##
class ActionSocket(object):
    TTL=180
    def __init__(self):
        self.current_action=None
        self.in_buffer=""

    def attach_action(self,action):
        logging.debug("attach_action %s"%str(action))
        self.current_action=action
        self.feed_action()
        
    def on_close(self):
        if self.current_action:
            self.current_action.close(None)
    
    def on_read(self,data):
        self.in_buffer+=data
        self.feed_action()

    def retain_input(self,msg):
        self.in_buffer=msg+self.in_buffer

    def feed_action(self):
        if self.in_buffer and self.current_action:
            self.current_action.feed(self.in_buffer)
            self.in_buffer=""
##
##
##
class TelnetSocket(ActionSocket,PTYSocket):
    __metaclass__=SchemeSocketBase
    name="telnet"
    default_action="cli"
    scheme_id=TELNET
    def __init__(self,factory,access_profile):
        logging.debug("TelnetStream connecting '%s'"%access_profile.address)
        PTYSocket.__init__(self,factory,["/usr/bin/telnet",access_profile.address])
        ActionSocket.__init__(self)
##
##
##
class SSHSocket(ActionSocket,PTYSocket):
    __metaclass__=SchemeSocketBase
    name="ssh"
    default_action="cli"
    scheme_id=SSH
    def __init__(self,factory,access_profile):
        logging.debug("TelnetStream connecting '%s'"%access_profile.address)
        PTYSocket.__init__(self,factory,["/usr/bin/ssh","-o","StrictHostKeyChecking no","-l",access_profile.user,access_profile.address])
        ActionSocket.__init__(self)
##
##
##
class HTTPStream(ActionSocket,ConnectedTCPSocket):
    __metaclass__=SchemeSocketBase
    name="http"
    default_action="http"
    scheme_id=HTTP
    def __init__(self,factory,access_profile):
        logging.debug("HTTPStream connecting to %s:%d"%(access_profile.address,80))
        ConnectedTCPSocket.__init__(self,factory,access_profile.address,80)
        ActionSocket.__init__(self)