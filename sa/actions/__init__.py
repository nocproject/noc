##
## BaseAction implementation
## Action is a scenario executed upon stream
##
import logging,re

rx_ansi_escape=re.compile("\x1b\\[(\d+(;\d+)?)?[a-zA-Z]")

class BaseAction(object):
    ARGS=[]
    ALLOW_ROGUE_CHARS=True # Strip Profile.rogue_chars out of stream
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
        if self.ALLOW_ROGUE_CHARS and self.profile.rogue_chars:
            for rc in self.profile.rogue_chars:
                msg=msg.replace(rc,"")
        if self.profile.strip_ansi_escapes:
            msg=rx_ansi_escape.sub("",msg)
        logging.debug("%s feed: %s"%(str(self),repr(msg)))
        self.buffer+=msg
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
        
def get_action_class(name):
    module=__import__("noc."+name,globals(),locals(),["Action"])
    return getattr(module,"Action")