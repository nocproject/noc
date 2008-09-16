import logging,re
##
##
##
class Action(object):
    ARGS=[]
    def __init__(self,supervisor,task_id,stream,args=None):
        self.supervisor=supervisor
        self.task_id=task_id
        self.profile=stream.profile
        self.stream=stream
        self.fsm=None
        self.args={}
        self.buffer=""
        self.result=""
        self.to_collect_result=False
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
        logging.debug("%s close(%s)"%(str(self),status))
        if self.buffer:
            self.stream.retain_input(self.buffer)
        self.stream.attach_action(None)
        self.supervisor.on_action_close(self,status)
    
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
    
    def feed(self,msg):
        if self.profile.rogue_chars:
            for rc in self.profile.rogue_chars:
                msg=msg.replace(rc,"")
        logging.debug("%s feed: %s"%(str(self),msg.replace("\n","\\n")))
        self.buffer+=msg
        if self.fsm:
            for rx,action in self.fsm:
                match=rx.search(self.buffer)
                if match:
                    logging.debug("FSM MATCH: %s"%rx.pattern)
                    if self.to_collect_result:
                        self.result+=self.buffer[:match.start(0)]
                    self.buffer=self.buffer[match.end(0):]
                    self.set_fsm(action(match))
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

## CLISessingAction:
## Perform basic login
## 
class CLISessionAction(Action):
    ARGS=["user","password","commands"]
    def prepare_action(self):
        if self.args["user"] is None:
            self.args["user"]=self.stream.user
        if self.args["password"] is None:
            self.args["password"]=self.stream.password
        self.commands=self.args["commands"][:]
        self.set_fsm([
            (self.profile.pattern_username, self.s_username),
            (self.profile.pattern_password, self.s_password),
            (self.profile.pattern_prompt,   self.s_command),
        ])
        
    def s_username(self,match):
        self.submit(self.args["user"])
        return [
            (self.profile.pattern_password, self.s_password),
            (self.profile.pattern_prompt,   self.s_command),
        ]
        
    def s_password(self,match):
        self.submit(self.args["password"])
        return [
            (self.profile.pattern_prompt,   self.s_command),
            (self.profile.pattern_username, "FAILURE"),
            (self.profile.pattern_password, "FAILURE"),
        ]
        
    def s_command(self,match):
        if len(self.commands)==0:
            self.close(True)
            return
        self.to_collect_result=True
        c=self.commands.pop(0)
        self.submit(c)
        if len(self.commands):
            return [
                (self.profile.pattern_more,   self.s_more),
                (self.profile.pattern_prompt, self.s_command),
                ]
        else:
            return [
                (self.profile.pattern_more,   self.s_more),
                (self.profile.pattern_prompt, "SUCCESS"),
                ]
        
    def s_more(self,match):
        self.stream.write(self.profile.command_more)
        return [
            (self.profile.pattern_more, self.s_more),
            (self.profile.pattern_prompt, self.s_command),
            ]