##
## Object resolver supervisor
##
from noc.peer.whois import Whois
from noc.lib.validators import is_asn,is_cidr
from noc.lib.nbsocket import SocketFactory
import sets,logging

class AS(object):
    def __init__(self,parent,name):
        self.parent=parent
        self.name=name
        self.prefixes=sets.Set([])
        self.parent.ases[self.name]=self
        self.as_sets=sets.Set([])
        self.is_new=True
        logging.debug("Creating %s"%self.name)
        
    def __repr__(self):
        return self.name
        
    def resolve(self):
        if self.is_new:
            logging.debug("Resolving %s"%self)
            self.parent.schedule_whois("-i origin %s"%self.name,self.add_prefixes,["route"])
            self.is_new=False
        
    def add_prefixes(self,prefixes):
        logging.debug("Add %s to %s"%(prefixes,self.name))
        for k,v in prefixes:
            if is_cidr(v):
                self.prefixes.add(v)
        for as_set in self.as_sets:
            as_set.add_prefixes(self.prefixes)
                
    def attach_to_asset(self,as_set):
        as_set.add_prefixes(self.prefixes)
        self.as_sets.add(as_set)
        
                
class ASSet(object):
    def __init__(self,parent,name):
        self.parent=parent
        self.name=name
        self.members=sets.Set([])
        self.parent.as_sets[self.name]=self
        self.prefixes=sets.Set([])
        self.as_sets=sets.Set([])
        self.is_new=True
        logging.debug("Creating %s"%self.name)
        
    def __repr__(self):
        return self.name
        
    def resolve(self):
        if not self.is_new:
            return
        logging.debug("Resolving %s"%self)
        self.is_new=False
        if is_asn(self.name[2:]):
            a=self.parent.create_as(self.name)
            self.add_member(a)
            a.attach_to_asset(self)
            a.resolve()
        else:
            self.parent.schedule_whois("%s"%self.name,self.add_members,["members"])
            
    def add_members(self,members):
        logging.debug("Add %s to %s"%(str(members),self))
        ms=sets.Set([])
        for k,v in members:
            ms.update([x.strip().upper() for x in v.split(",")])
        for m in ms:
            if is_asn(m):
                a=self.parent.create_as(m)
                self.add_member(a)
                a.attach_to_asset(self)
                a.resolve()
            else:
                a=self.parent.create_as_set(m)
                a.attach_to_asset(self)
                a.resolve()
                    
    def add_prefixes(self,prefixes):
        logging.debug("Add %s to %s"%(prefixes,self.name))
        if not prefixes.issubset(self.prefixes):
            self.prefixes.update(prefixes)
            for as_set in self.as_sets:
                as_set.add_prefixes(prefixes)
            
    def attach_to_asset(self,as_set):
        logging.debug("Attaching %s to %s"%(self,as_set))
        self.as_sets.add(as_set)
        as_set.add_prefixes(self.prefixes)
        as_set.members.update(self.members)
        
    def add_member(self,a):
        if a not in self.members:
            self.members.add(a)
            for as_set in self.as_sets:
                as_set.add_member(a)
            

class Resolver(object):
    def __init__(self,whois_concurrency=5):
        self.whois_queue=[]
        self.ases={}
        self.as_sets={}
        self.whois_concurrency=whois_concurrency
        
    def create_as(self,name):
        if name in self.ases:
            return self.ases[name]
        else:
            return AS(self,name)
            
    def create_as_set(self,name):
        if name in self.as_sets:
            return self.as_sets[name]
        else:
            return ASSet(self,name)
        
    def schedule_whois(self,query,callback,fields=None):
        logging.debug("Scheduliung whois query: %s"%query)
        self.whois_queue.append((query,callback,fields))
    #
    # Resolves a list of as-sets and returns a hash of
    # name -> (members,prefixes)
    #
    def resolve(self,as_sets):
        factory=SocketFactory()
        for x in as_sets:
            if not x in self.ases:
                a=ASSet(self,x)
                a.resolve()
        while self.whois_queue or len(factory):
            while self.whois_queue and len(factory)<self.whois_concurrency:
                q,c,f=self.whois_queue.pop(0)
                Whois(factory,q,c,f)
            factory.loop()
        r={}
        for n,a in self.as_sets.items():
            r[n]=(a.members,a.prefixes)
        return r

def test(as_sets):
    logging.basicConfig(level=logging.DEBUG)
    r=Resolver()
    print r.resolve(as_sets)