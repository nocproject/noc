##
## Finite State Machine
## 
import time,logging

class FSM(object):
    FSM_NAME="FSM"
    DEFAULT_STATE="DEFAULT" # Running state
    STATES={}               # STATE -> { EVENT -> New State}
    def __init__(self):
        self._current_state=None
        self._state_enter_time=None
        self._state_exit_time=None
        self.set_state(self.DEFAULT_STATE)
        
    def __debug(self,message):
        logging.debug("%s::%s %s"%(self.FSM_NAME,self._current_state,message))
        
    def get_state_handler(self,state,event):
        name="on_%s_%s"%(state,event)
        try:
            return getattr(self,name)
        except:
            return None
            
    def call_state_handler(self,state,event):
        h=self.get_state_handler(state,event)
        if h:
            h()
            
    def get_state(self):
        return self._current_state
        
    def set_state(self,state):
        self.__debug("==> %s"%state)
        if state not in self.STATES:
            raise Exception("Invalid state %s"%state)
        if self._current_state:
            self.call_state_handler(self._current_state,"exit")
        self._current_state=state
        self._state_enter_time=time.time()
        self._state_exit_time=None
        self.call_state_handler(state,"enter")
    
    def set_timeout(self,timeout):
        self.__debug("set_timeout(%s)"%timeout)
        self._state_exit_time=time.time()+timeout
    ##
    ## Send event to FSM
    ##
    def event(self,event):
        self.__debug("event(%s)"%event)
        if event not in self.STATES[self._current_state]:
            raise Exception("Invalid event '%s' in state '%s'"%(event,self._current_state))
        self.call_state_handler(self._current_state,event)
        self.set_state(self.STATES[self._current_state][event])
    ##
    ## Method should be called in event loop every second to process timeout and tick events
    ##
    def tick(self):
        if self._state_exit_time and self._state_exit_time<time.time():
            self.__debug("Timeout expired")
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
