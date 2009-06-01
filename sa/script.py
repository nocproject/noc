# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.fsm import StreamFSM
from noc.lib.ecma48 import strip_control_sequences
from noc.lib.registry import Registry
from noc.lib.nbsocket import PTYSocket
from noc.lib.debug import format_frames,get_traceback_frames
from noc.sa.protocols.sae_pb2 import TELNET,SSH,HTTP
from noc.sa.profiles import profile_registry
import logging,re,threading,Queue,urllib,httplib,random,base64,hashlib,cPickle,sys,time

try:
    from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
    from pysnmp.carrier.asynsock.dgram import udp
    from pyasn1.codec.ber import encoder, decoder
    from pysnmp.proto import api
    HAS_SNMP=True
except ImportError:
    HAS_SNMP=False


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
class ScriptProxy(object):
    def __init__(self,parent):
        self._parent=parent
    def __getattr__(self,name):
        return ScriptCallProxy(self._parent,self._parent.profile.scripts[name])

class ScriptCallProxy(object):
    def __init__(self,parent,script):
        self.parent=parent
        self.script=script
        
    def __call__(self,**kwargs):
        s=self.script(self.parent.profile,self.parent.activator,self.parent.access_profile,parent=self.parent,**kwargs)
        return s.guarded_run()
##
##
##
class ScriptRegistry(Registry):
    name="ScriptRegistry"
    subdir="profiles"
    classname="Script"
    apps=["noc.sa"]
    exclude=["highlight"]
    def register_generics(self):
        for c in [c for c in self.classes.values() if c.name and c.name.startswith("Generic.") and c.requires]:
            g,name=c.name.split(".")
            for p in profile_registry.classes:
                s_name=p+"."+name
                # Do not register generic when specific exists
                if s_name in self.classes:
                    continue
                to_register=True
                for r_name,r_interface in c.requires:
                    rs_name=p+"."+r_name
                    if rs_name not in self.classes or not self.classes[rs_name].implements_interface(r_interface):
                        to_register=False
                        break
                if to_register:
                    logging.debug("Script Registry: Register generic %s"%s_name)
                    self.classes[s_name]=c
                    profile_registry[p].scripts[name]=c
    def register_all(self):
        super(ScriptRegistry,self).register_all()
        self.register_generics()

script_registry=ScriptRegistry()
##
##
##
class ScriptBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        m.implements=[c() for c in m.implements]
        script_registry.register(m.name,m)
        if m.name and not m.name.startswith("Generic."):
            pv,pos,sn=m.name.split(".",2)
            profile_registry["%s.%s"%(pv,pos)].scripts[sn]=m
        return m
##
##
##
class Script(threading.Thread):
    __metaclass__=ScriptBase
    name=None
    description=None
    # Interfaces list. Each element of list must be Interface subclass
    implements=[]
    # Scripts required by generic script.
    # For common scripts - empty list
    # For generics - list of pairs (script_name,interface)
    requires=[]
    # Constants
    TELNET=scheme_id["telnet"]
    SSH=scheme_id["ssh"]
    HTTP=scheme_id["http"]

    def __init__(self,profile,activator,access_profile,parent=None,**kwargs):
        self.parent=parent
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
        self.profile=profile
        self.cli_provider=None
        self.http=HTTPProvider(self.access_profile)
        if HAS_SNMP:
            self.snmp=SNMPProvider(self.access_profile)
        else:
            self.snmp=None
        self.status=False
        self.result=None
        self.error_traceback=None
        self.strip_echo=True
        self.kwargs=kwargs
        self.scripts=ScriptProxy(self)
    
    @classmethod
    def implements_interface(cls,interface):
        for i in cls.implements:
            if type(i)==interface:
                return True
        return False
        
    def debug(self,msg):
        logging.debug("[%s] %s"%(self.debug_name,msg))
        
    def guarded_run(self):
        self.debug("Guarded run")
        # Enforce interface type checking
        for i in self.implements:
            self.kwargs=i.clean(**self.kwargs)
        # Calling script body
        result=self.execute(**self.kwargs)
        # Enforce interface result checking
        for i in self.implements:
            result=i.clean_result(result)
        self.debug("Script returns with result: %s"%result)
        return result
        
    def serialize_result(self,result):
        return cPickle.dumps(result)
        
    def run(self):
        self.debug("Running")
        try:
            self.result=self.serialize_result(self.guarded_run())
        except:
            t,v,tb=sys.exc_info()
            r=[str(t),str(v)]
            r+=[format_frames(get_traceback_frames(tb))]
            self.error_traceback="\n".join(r)
            self.debug("Script traceback:\n%s"%self.error_traceback)
        self.debug("Closing")
        if self.cli_provider:
            self.activator.request_call(self.cli_provider.close)
        self.activator.on_script_exit(self)
        
    def execute(self,**kwargs):
        return None
    
    def request_cli_provider(self):
        if self.parent:
            self.cli_provider=self.parent.request_cli_provider()
        elif self.cli_provider is None:
            self.debug("Running new provider")
            if self.access_profile.scheme==TELNET:
                s_class=CLITelnetSocket
            elif self.access_profile.scheme==SSH:
                s_class=CLISSHSocket
            else:
                raise Exception("Invalid access scheme '%d' for CLI"%self.access_profile.scheme)
            self.cli_provider=s_class(self.activator.factory,self.profile,self.access_profile)
            self.cli_provider.queue.get(block=True) # Wait until provider in PROMPT
            self.debug("CLI Provider is ready")
        return self.cli_provider
        
    def cli(self,cmd):
        self.debug("cli(%s)"%cmd)
        self.request_cli_provider()
        self.cli_provider.submit(cmd)
        data=self.cli_provider.queue.get(block=True)
        if self.strip_echo and data.lstrip().startswith(cmd):
            data=self.strip_first_lines(data.lstrip())
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
    ## Expands expressions like "1,2,5-7" to [1,2,5,6,7]
    ##
    def expand_rangelist(self,s):
        result={}
        for x in s.split(","):
            x=x.strip()
            if x=="":
                continue
            if "-" in x:
                l,r=[int(y) for y in x.split("-")]
                if l>r:
                    x=r
                    r=l
                    l=x
                for i in range(l,r+1):
                    result[i]=None
            else:
                result[int(x)]=None
        return sorted(result.keys())
##
##
##
class TimeOutError(Exception): pass
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
            "PASSWORD"            : "SUPER_PASSWORD",
            "PROMPT"              : "PROMPT",
        },
        "PROMPT":{
            "PROMPT"      : "PROMPT",
            "PAGER"       : "PROMPT",
            "PAGER_START" : "PROMPT",
            "PAGER_END"   : "PROMPT",
            "CLOSE"       : "CLOSED",
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
        self.collected_data=""
        self.prompt_patters=[x for x in [self.profile.pattern_more,self.profile.pattern_more_start,self.profile.pattern_more_end] if x]
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
        if self.profile.pattern_unpriveleged_prompt:
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
        if self.profile.pattern_unpriveleged_prompt:
            p+=[
                (self.profile.pattern_unpriveleged_prompt,"UNPRIVELEGED_PROMPT"),
            ]
        p+=[
            (self.profile.pattern_username, "USERNAME"),
            (self.profile.pattern_password, "PASSWORD")
            ]
        self.set_patterns(p)
        self.submit(self.access_profile.password)
        
    def on_UNPRIVELEGED_PROMPT_enter(self):
        self.set_patterns([
            (self.profile.pattern_prompt,   "PROMPT"),
            (self.profile.pattern_password, "PASSWORD"),
        ])
        self.submit(self.profile.command_super)
    
    def on_SUPER_PASSWORD_enter(self):
        self.set_patterns([
            (self.profile.pattern_prompt, "PROMPT"),
            (self.profile.pattern_password, "PASSWORD")
        ])
        sp=self.access_profile.super_password
        if not sp:
            sp=""
        self.submit(sp)
        
    def on_PROMPT_enter(self):
        if not self.is_ready:
            self.queue.put(None) # Signal provider passing into PROMPT state
            self.is_ready=True
        p=[
            (self.profile.pattern_prompt, "PROMPT"),
            (self.profile.pattern_more,   "PAGER"),
            ]
        if self.profile.pattern_more_start:
            p+=[(self.profile.pattern_more_start, "PAGER_START")]
        if self.profile.pattern_more_end:
            p+=[(self.profile.pattern_more_end, "PAGER_END")]
        self.set_patterns(p)
        
    def on_PROMPT_match(self,data,match):
        if match.re.pattern in self.prompt_patters:
            self.collected_data+=data
        elif match.re.pattern==self.profile.pattern_prompt:
            self.queue.put(self.collected_data+data)
            self.collected_data=""
        
    def on_PROMPT_PAGER(self):
        self.write(self.profile.command_more)
    
    def on_PROMPT_PAGER_START(self):
        if self.profile.command_more_start is None:
            self.write(self.profile.command_more)
        else:
            self.write(self.profile.command_more_start)
    
    def on_PROMPT_PAGER_END(self):
        if self.profile.command_more_end is None:
            self.write(self.profile.command_more)
        else:
            self.write(self.profile.command_more_end)

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
        self.authorization=None
    
    def request(self,method,path,params=None,headers={}):
        if self.authorization:
            headers["Authorization"]=self.authorization
        conn=httplib.HTTPConnection(self.access_profile.address)
        conn.request(method,path,params,headers)
        response=conn.getresponse()
        try:
            if response.status==200:
                return response.read()
            elif response.status==401 and self.authorization is None:
                self.set_authorization(response.getheader("www-authenticate"),method,path)
                return self.request(method,path,params,headers)
            else:
                raise Exception("HTTP Error: %s"%response.status)
        finally:
            conn.close()
            
    def set_authorization(self,auth,method,path):
        scheme,data=auth.split(" ",1)
        scheme=scheme.lower()
        d={}
        for s in data.split(","):
            s=s.strip()
            if "=" in s:
                k,v=s.split("=",1)
                if v.startswith("\"") and v.endswith("\""):
                    v=v[1:-1]
                d[k]=v
            else:
                d[s]=None
        if scheme=="basic":
            self.authorization="Basic %s"%base64.b64encode("%s:%s"%(self.access_profile.user,self.access_profile.password)).strip()
        elif scheme=="digest":
            H = lambda x: hashlib.md5(x).hexdigest()
            KD= lambda x,y: H("%s:%s"%(x,y))
            A1="%s:%s:%s"%(self.access_profile.user,d["realm"],self.access_profile.password)
            A2="%s:%s"%(method,path)
            f={
                "username": self.access_profile.user,
                "realm"   : d["realm"],
                "nonce"   : d["nonce"],
                "uri"     : path,
            }
            if "qop" not in d:
                noncebit="%s:%s"%(d["nonce"],H(A2))
            elif d["qop"]=="auth":
                nc="00000001"
                cnonce=H(str(random.random()))
                f["nc"]=nc
                f["cnonce"]=cnonce
                f["qop"]=d["qop"]
                noncebit="%s:%s:%s:%s:%s"%(d["nonce"],nc,cnonce,d["qop"],H(A2))
            else:
                raise Exception("qop not supported: %s"%d["qop"])
            f["response"]=KD(H(A1),noncebit)
            self.authorization="Digest "+", ".join(["%s=\"%s\""%(k,v) for k,v in f.items()])
        else:
            raise Exception("Unknown auth method: %s"%scheme)
    
    def get(self,path,params=None,headers={}):
        return self.request("GET",path)
    
    def post(self,path,params=None,headers={}):
        if params:
            params=urllib.urlencode(params)
            headers["Content-Type"]="application/x-www-form-urlencoded"
        return self.request("POST",path,params,headers)
##
##
##
class SNMPProvider(object):
    TimeOutError=TimeOutError
    def __init__(self,access_profile):
        self.access_profile=access_profile
        self.queue=Queue.Queue()
    
    def str_to_oid(self,s):
        return tuple([int(x) for x in s.split(".")])
        
    def get(self,oid):
        self.run_get(oid)
        return self.queue.get(block=True)
    
    def run_get(self,oid):
        logging.debug("SNMP GET %s"%oid)
        # Protocol version to use
        protocol = api.protoModules[api.protoVersion1]
        # Build PDU
        req_pdu =  protocol.GetRequestPDU()
        protocol.apiPDU.setDefaults(req_pdu)
        protocol.apiPDU.setVarBinds(req_pdu, ((self.str_to_oid(oid), protocol.Null()),))
        # Build message
        req = protocol.Message()
        protocol.apiMessage.setDefaults(req)
        protocol.apiMessage.setCommunity(req, self.access_profile.snmp_ro)
        protocol.apiMessage.setPDU(req, req_pdu)
        def timer_callback(timeNow, start_time=time.time()):
            if timeNow - start_time > 3:
                raise TimeOutError
        def recv_callback(transportDispatcher, transportDomain, transportAddress, msg, req_pdu=req_pdu):
            while msg:
                rsp_msg, msg = decoder.decode(msg, asn1Spec=protocol.Message())
                rspPDU = protocol.apiMessage.getPDU(rsp_msg)
                # Match response to request
                if protocol.apiPDU.getRequestID(req_pdu)==protocol.apiPDU.getRequestID(rspPDU):
                    # Check for SNMP errors reported
                    errorStatus = protocol.apiPDU.getErrorStatus(rspPDU)
                    #if errorStatus:
                    #    print errorStatus.prettyPrint()
                    #else:
                    for oid, val in protocol.apiPDU.getVarBinds(rspPDU):
                        self.queue.put(str(val))
                    transportDispatcher.jobFinished(1)
            return msg
        transportDispatcher = AsynsockDispatcher()
        transportDispatcher.registerTransport(udp.domainName, udp.UdpSocketTransport().openClientMode())
        transportDispatcher.registerRecvCbFun(recv_callback)
        transportDispatcher.registerTimerCbFun(timer_callback)
        transportDispatcher.sendMessage(encoder.encode(req), udp.domainName, (self.access_profile.address, 161))
        transportDispatcher.jobStarted(1)
        transportDispatcher.runDispatcher()
        transportDispatcher.closeDispatcher()
