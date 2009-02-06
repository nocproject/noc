# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Finite State Machine
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import time,logging,re

##
## State checking decorator
##
def check_state(state):
    def check_returns(f):
        def new_f(self,*args, **kwds):
            assert self._current_state==state,\
                "Function '%s' cannot be called from state '%s' ('%s' required)"%(f.func_name,self._current_state,state)
            return f(self,*args, **kwds)
        new_f.func_name = f.func_name
        return new_f
    return check_returns

##
## Finite state machine class
##
class FSM(object):
    FSM_NAME="FSM"
    DEFAULT_STATE="DEFAULT" # Running state
    STATES={}               # STATE -> { EVENT -> New State}
    def __init__(self):
        self._current_state=None
        self._state_enter_time=None
        self._state_exit_time=None
        self.set_state(self.DEFAULT_STATE)

    def debug(self,msg):
        logging.debug("[%s(0x%x)]<%s> %s"%(self.__class__.__name__,id(self),self.get_state(),msg))

    def get_state_handler(self,state,event):
        name="on_%s_%s"%(state,event)
        try:
            return getattr(self,name)
        except:
            return None
            
    def call_state_handler(self,state,event,*args):
        h=self.get_state_handler(state,event)
        if h:
            apply(h,args)
            
    def get_state(self):
        return self._current_state
        
    def set_state(self,state):
        if state==self._current_state:
            return
        self.debug("==> %s"%state)
        if state not in self.STATES:
            raise Exception("Invalid state %s"%state)
        if self._current_state:
            self.call_state_handler(self._current_state,"exit")
        self._current_state=state
        self._state_enter_time=time.time()
        self._state_exit_time=None
        self.call_state_handler(state,"enter")
    
    def set_timeout(self,timeout):
        self.debug("set_timeout(%s)"%timeout)
        self._state_exit_time=time.time()+timeout
    ##
    ## Send event to FSM
    ##
    def event(self,event):
        self.debug("event(%s)"%event)
        if event not in self.STATES[self._current_state]:
            raise Exception("Invalid event '%s' in state '%s'"%(event,self._current_state))
        self.call_state_handler(self._current_state,event)
        self.set_state(self.STATES[self._current_state][event])
    ##
    ## Method should be called in event loop every second to process timeout and tick events
    ##
    def tick(self):
        if self._state_exit_time and self._state_exit_time<time.time():
            self.debug("Timeout expired")
            self.event("timeout")
        else:
            self.call_state_handler(self._current_state,"tick")
    
    ##
    ## Make nice GraphViz .dot chart
    ##
    @classmethod
    def get_dot(cls):
        r=["digraph {"]
        r+=["label=\"%s state machine\";"%cls.FSM_NAME]
        for s in cls.STATES:
            if s==cls.DEFAULT_STATE:
                r+=["%s [shape=\"doublecircle\"];"%s]
            else:
                r+=["%s;"%s]
            transforms={}
            for e,ns in cls.STATES[s].items():
                if ns in transforms:
                    transforms[ns].append(e)
                else:
                    transforms[ns]=[e]
            for ns,events in transforms.items():
                r+=["%s -> %s [label=\"%s\"];"%(s,ns,",\\n".join(events))]
        r+=["}",""]
        return "\n".join(r)
    @classmethod
    def write_dot(cls,path):
        f=open(path,"w")
        f.write(cls.get_dot())
        f.close()
##
## StreamFSM also changes state on input stream conditions
##
class StreamFSM(FSM):
    def __init__(self):
        self.patterns=[]
        self.in_buffer=""
        super(StreamFSM,self).__init__()
        
    def debug(self,msg):
        logging.debug("[%s(0x%x)]<%s> %s"%(self.__class__.__name__,id(self),self.get_state(),msg))
        
    def set_patterns(self,patterns):
        self.debug("set_patterns(%s)"%repr(patterns))
        self.patterns=[(re.compile(x,re.DOTALL|re.MULTILINE),y) for x,y in patterns]
        
    def feed(self,data,cleanup=None):
        self.debug("feed: %s"%repr(data))
        self.in_buffer+=data
        if cleanup:
            self.in_buffer=cleanup(self.in_buffer)
        while self.in_buffer and self.patterns:
            matched=False
            for rx,event in self.patterns:
                match=rx.search(self.in_buffer)
                if match:
                    matched=True
                    self.debug("match '%s'"%rx.pattern)
                    self.call_state_handler(self._current_state,"match",self.in_buffer[:match.start(0)],match)
                    self.in_buffer=self.in_buffer[match.end(0):]
                    self.event(event) # Change state
                    break
            if not matched:
                break
