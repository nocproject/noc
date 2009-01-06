from noc.lib.fsm import StreamFSM
from noc.lib.ecma48 import strip_control_sequences
from noc.lib.registry import Registry
from noc.lib.nbsocket import PTYSocket
from noc.sa.protocols.sae_pb2 import TELNET,SSH,HTTP
from noc.sa.profiles import profile_registry
import logging,re,threading,Queue,httplib,urllib


##
##
##
scheme_id={
    "telnet" : TELNET,
    "ssh"    : SSH,
    "http"   : HTTP,
}

##
##
##
class ScriptRegistry(Registry):
    name="ScriptRegistry"
    subdir="profiles"
    classname="Script"
    apps=["noc.sa"]

script_registry=ScriptRegistry()
##
##
##
class ScriptBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        script_registry.register(m.name,m)
        return m
##
##
##
class Script(threading.Thread):
    __metaclass__=ScriptBase
    name=None
    description=None
    TELNET=scheme_id["telnet"]
    SSH=scheme_id["ssh"]
    HTTP=scheme_id["http"]

    def __init__(self,activator,access_profile,**kwargs):
        self.access_profile=access_profile
        if self.access_profile.address:
            p=self.access_profile.address
        elif self.access_profile.path:
            p=self.access_profile.path
        else:
            p="<unknown>"
        self.debug_name="script-%s-%s"%(p,self.name)
        super(Script,self).__init__(name=self.debug_name,kwargs=kwargs)
        self.activator=activator
        pv,pos,sn=self.name.split(".",2)
        self.profile=profile_registry["%s.%s"%(pv,pos)]()
        self.cli_provider=None
        self.http=HTTPProvider(self.access_profile)
        self.status=False
        self.result=None
        self.strip_echo=True
        
    def debug(self,msg):
        logging.debug("[%s] %s"%(self.debug_name,msg))
        
    def run(self,**kwargs):
        self.debug("Running")
        self.result=self.execute(**kwargs)
        self.status=True
        self.debug("Closing")
        if self.cli_provider:
            #self.cli_provider.close()
            self.activator.request_call(self.cli_provider.close)
        self.debug("Script terminated with result: %s"%self.result)
        self.activator.on_script_exit(self)
        
    def execute(self,**kwargs):
        return None
    
    def cli(self,cmd):
        self.debug("cli(%s)"%cmd)
        if self.cli_provider is None:
            self.debug("Running new provider")
            if self.access_profile.scheme==TELNET:
                s_class=CLITelnetSocket
            elif self.access_profile.scheme==SSH:
                s_class=CLISSHSocket
            else:
                raise Exception("Invalid access scheme '%d' for CLI"%self.access_profile.scheme)
            self.cli_provider=s_class(self.activator.factory,self.profile,self.access_profile)
            self.cli_provider.queue.get(block=True) # Wait until provider in PROMPT
            self.debug("Provider is ready")
        self.cli_provider.submit(cmd)
        data=self.cli_provider.queue.get(block=True)
        if self.strip_echo and data.startswith(cmd):
            data=self.strip_first_lines(data)
        self.debug("cli() returns:\n---------\n%s\n---------"%data)
        return data
    ##
    ## Clean up config from all unnecessary trash
    ##
    def cleaned_config(self,config):
        return self.profile.cleaned_config(config)
    ##
    ##
    ##
    def strip_first_lines(self,text,lines=1):
        t=text.split("\n")
        if len(t)<=lines:
            return ""
        else:
            return "\n".join(t[lines:])
    
##
##
##
class CLI(StreamFSM):
    FSM_NAME="CLI"
    DEFAULT_STATE="START"
    STATES={
        "START":{
            "USERNAME"            : "USERNAME",
            "PASSWORD"            : "PASSWORD",
            "UNPRIVELEGED_PROMPT" : "UNPRIVELEGED_PROMPT",
            "PROMPT"              : "PROMPT"
        },
        "USERNAME":{
            "USERNAME"            : "FAILURE",
            "PASSWORD"            : "PASSWORD",
            "UNPRIVELEGED_PROMPT" : "UNPRIVELEGED_PROMPT",
            "PROMPT"              : "PROMPT"
        },
        "PASSWORD":{
            "USERNAME"            : "FAILURE",
            "PASSWORD"            : "FAILURE",
            "UNPRIVELEGED_PROMPT" : "UNPRIVELEGED_PROMPT",
            "PROMPT"              : "PROMPT"
        },
        "SUPER_PASSWORD" : {
            "UNPRIVELEGED_PROMPT" : "FAILURE",
            "PASSWORD"            : "FAILURE",
            "PROMPT"              : "PROMPT",
        },
        "UNPRIVELEGED_PROMPT":{
            "PASSWORD"            : "SUPER_PASSWORD"
        },
        "PROMPT":{
            "PROMPT": "PROMPT",
            "PAGER" : "PROMPT",
            "CLOSE" : "CLOSED",
        },
        "FAILURE":{
        },
        "CLOSED":{
        }
    }
    
    def __init__(self,profile,access_profile):
        self.profile=profile
        self.access_profile=access_profile
        self.queue=Queue.Queue()
        self.is_ready=False
        StreamFSM.__init__(self)
    
    def on_read(self,data):
        self.debug("on_read: %s"%repr(data))
        if self.profile.rogue_chars:
            for rc in self.profile.rogue_chars:
                data=data.replace(rc,"")
        self.feed(data,cleanup=strip_control_sequences)
    
    def submit(self,msg):
        self.debug("submit(%s)"%repr(msg))
        self.write(msg+self.profile.command_submit)
    
    def on_START_enter(self):
        p=[
            (self.profile.pattern_username,"USERNAME"),
            (self.profile.pattern_password,"PASSWORD"),
        ]
        if self.profile.pattern_unpriveleged_prompt and self.access_profile.super_password:
            p+=[
                (self.profile.pattern_unpriveleged_prompt,"UNPRIVELEGED_PROMPT"),
            ]
        p+=[
            (self.profile.pattern_prompt,"PROMPT"),
        ]
        self.set_patterns(p)
    
    def on_USERNAME_enter(self):
        self.set_patterns([
            (self.profile.pattern_password, "PASSWORD"),
            (self.profile.pattern_prompt,   "PROMPT"),
        ])
        self.submit(self.access_profile.user)
        
    def on_PASSWORD_enter(self):
        p=[(self.profile.pattern_prompt, "PROMPT")]
        if self.profile.pattern_unpriveleged_prompt and self.access_profile.super_password:
            p+=[
                (self.profile.pattern_unpriveleged_prompt,"UNPRIVELEGED_PROMPT"),
            ]
        p+=[
            (self.profile.pattern_username, "FAILURE"),
            (self.profile.pattern_password, "FAILURE")
            ]
        self.set_patterns(p)
        self.submit(self.access_profile.password)
        
    def on_UNPRIVELEGED_PROMPT_enter(self):
        self.set_patterns([
            (self.profile.pattern_prompt,   self.s_command),
            (self.profile.pattern_password, self.s_super_password),
        ])
        self.submit(self.profile.command_super)
    
    def on_SUPER_PASWORD_enter(self):
        self.set_patterns([
            (self.profile.pattern_prompt, "PROMPT"),
            (self.profile.pattern_password, "PASSWORD")
        ])
        self.submit(self.access_profile.super_password)
        
    def on_PROMPT_enter(self):
        if not self.is_ready:
            self.queue.put(None) # Signal provider passing into PROMPT state
            self.is_ready=True
        self.set_patterns([(self.profile.pattern_prompt, "PROMPT")])
        
    def on_PROMPT_match(self,data,match):
        self.queue.put(data)
    
    def on_FAILURE_enter(self):
        self.set_patterns([])

##
##
##
class ScriptSocket(object):pass
#
##
##
class CLITelnetSocket(ScriptSocket,CLI,PTYSocket):
    def __init__(self,factory,profile,access_profile):
        logging.debug("CLITelnetSocket connecting '%s'"%access_profile.address)
        CLI.__init__(self,profile,access_profile)
        PTYSocket.__init__(self,factory,["/usr/bin/telnet",access_profile.address])
        ScriptSocket.__init__(self)
##
##
##
class CLISSHSocket(ScriptSocket,CLI,PTYSocket):
    def __init__(self,factory,profile,access_profile):
        logging.debug("CLISSHSocket connecting '%s'"%access_profile.address)
        CLI.__init__(self,profile,access_profile)
        PTYSocket.__init__(self,factory,["/usr/bin/ssh","-o","StrictHostKeyChecking no","-l",access_profile.user,access_profile.address])
        ScriptSocket.__init__(self)
##
##
##
class HTTPProvider(object):
    def __init__(self,access_profile):
        self.access_profile=access_profile
    def get(self,path):
        conn=httplib.HTTPConnection(self.access_profile.address)
        conn.request("GET",path)
        response=conn.getresponse()
        try:
            if response.status==200:
                return response.read()
        finally:
            conn.close()
    def post(self,path,params=None):
        headers={}
        if params:
            params=urllib.urlencode(params)
            headers={"Content-type": "application/x-www-form-urlencoded"}
        conn=httplib.HTTPConnection(self.access_profile.address)
        conn.request("POST",path,params,headers)
        response=conn.getresponse()
        try:
            if response.status==200:
                return response.read()
        finally:
            conn.close()
