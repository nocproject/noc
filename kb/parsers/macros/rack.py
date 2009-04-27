# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## rack macro
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.kb.parsers.macros import Macro as MacroBase
import xml.parsers.expat
##
##
##
class RackSet(object):
    def __init__(self,id):
        self.id=id
        self.racks=[]
    def render_html(self):
        return "<div>%s</div>"%"\n".join([r.render_html() for r in self.racks])
##
##
##
class Rack(object):
    def __init__(self,rackset,id,height):
        self.rackset=rackset
        self.id=id
        self.height=height
        self.rackset.racks.append(self)
        self.allocations=[]
    
    def render_html(self):
        allocations=sorted(self.allocations,lambda x,y: -cmp(x.position,y.position))
        print allocations
        sp=[]
        if len(allocations)==0:
            sp+=[(self.height,self.height,True,None)]
        else:
            a=allocations.pop(0)
            empty_top=self.height-a.position-a.height+1
            if empty_top:
                sp+=[(self.height,empty_top,True,None)]
            sp+=[(a.position+a.height-1,a.height,False,a.id)]
            while allocations:
                last_a=a
                a=allocations.pop(0)
                empty_top=last_a.position-a.height-a.position
                if empty_top:
                    sp+=[(last_a.position-1,empty_top,True,None)]
                sp+=[(a.height+a.position-1,a.height,False,a.id)]
            if a.position>1:
                sp+=[(a.position-1,a.position-1,True,None)]
        out=["<table class='rack'>"]
        if self.id:
            out+=["<caption>%s</caption>"%self.id]
        pos=self.height
        print sp
        while sp:
            top,height,is_empty,name=sp.pop(0)
            if name is None:
                name=""
            if is_empty:
                style='empty'
            else:
                style='occupied'
            if height>1:
                out+=["<tr><td rowspan='%d' class='%s'>%s</td><td class='ruler'>%d</td></tr>"%(height,style,name,pos)]
                pos-=1
                while pos>top-height:
                    out+=["<tr><td class='ruler'>%d</td></tr>"%pos]
                    pos-=1
            else:
                out+=["<tr><td class='%s'>%s</td><td class='ruler'>%d</td></tr>"%(style,name,pos)]
                pos-=1
        out+=["</table>"]
        return "\n".join(out)
##
##
##
class Allocation(object):
    def __init__(self,rack,id,position,height):
        self.rack=rack
        self.id=id
        self.position=position
        self.height=height
        self.rack.allocations.append(self)
    
    def __repr__(self):
        return "Allocation: id=%s position=%s height=%s"%(self.id,self.position,self.height)
##
class XMLParser(object):
    def __init__(self,text):
        self.parser=xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler=self.start_element
        self.parser.EndElementHandler=self.end_element
        self.parser.CharacterDataHandler =self.char_data
        self.rackset=None
        self.last_rack=None
        self.parser.Parse("<?xml version='1.0'?>\n"+text)
    def start_element(self,name,attrs):
        if name=="rackset":
            self.rackset=RackSet(id=attrs.get("id",None))
        elif name=="rack":
            height=attrs.get("height","1U").upper()
            if height.endswith("U"):
                height=height[:-1]
            self.last_rack=Rack(self.rackset,id=attrs.get("id",None),height=int(height))
        elif name=="allocation":
            height=attrs.get("height","1U").upper()
            if height.endswith("U"):
                height=height[:-1]
            allocation=Allocation(self.last_rack,id=attrs.get("id",None),height=int(height),position=int(attrs.get("position",0)))
    def end_element(self,name): pass
    def char_data(self,name): pass

##
class Macro(MacroBase):
    name="rack"
    @classmethod
    def handle(cls,args,text):
        parser=XMLParser(text)
        return unicode(parser.rackset.render_html())
