# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## rack macro
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.kb.parsers.macros import Macro as MacroBase
import xml.parsers.expat
import re
from django.utils.html import escape

rx_link=re.compile(r"^(.*)\|(https?://.+)$")

def unroll_link(s):
    match=rx_link.match(s)
    if match:
        return "<a href='%s'>%s</a>"%(match.group(2),escape(match.group(1)).replace(r"\n","<br/>"))
    else:
        return s
##
## RackSet representation
##
class RackSet(object):
    def __init__(self,id,label):
        self.id=id
        self.racks=[]
        if label is None:
            self.label="bottom"
        else:
            self.label=label.lower()
    ##
    ## Return a list of allocations for a rack
    ## allocation is a tuple of: top position, height, is empty space, allocation
    ##
    def compile_allocations(self,rack):
        allocations=sorted(rack.allocations,lambda x,y: -cmp(x.position,y.position))
        sp=[]
        if len(allocations)==0:
            sp+=[(rack.height,rack.height,True,None)]
        else:
            a=allocations.pop(0)
            empty_top=rack.height-a.position-a.height+1
            if empty_top:
                sp+=[(rack.height,empty_top,True,None)]
            sp+=[(a.position+a.height-1,a.height,False,a)]
            while allocations:
                last_a=a
                a=allocations.pop(0)
                empty_top=last_a.position-a.height-a.position
                if empty_top:
                    sp+=[(last_a.position-1,empty_top,True,None)]
                sp+=[(a.height+a.position-1,a.height,False,a)]
            if a.position>1:
                sp+=[(a.position-1,a.position-1,True,None)]
        return sp
    ##
    ## Render RackSet contents to HTML
    ##
    def render_html(self):
        if len(self.racks)==0: # Empty rackset
            return u""
        #return "<div>%s</div>"%"\n".join([r.render_html() for r in self.racks])
        self.height=max([r.height for r in self.racks]) # RackSet height is a maximal height of the racks
        # Fill RackSet matrix
        # RSM is a hash: row -> column -> {"colspan","rowspan","style","text"}
        rsm={}
        for i in range(1,self.height+1):
            rsm[i]={}
            for j in range(len(self.racks)):
                rsm[i][j*2]=None
                rsm[i][j*2+1]={"class":"ruler","text":str(i)}
        # Remove the tops of the racks if necessary
        for j in range(len(self.racks)):
            rh=self.racks[j].height
            if rh<self.height:
                for i in range(self.height,rh,-1):
                    rsm[i][j*2]=None
                    rsm[i][j*2+1]=None
                rsm[self.height][j*2]={"colspan":2,"rowspan":self.height-rh,"class":"emptytop"}
        # Place allocations
        for j in range(len(self.racks)):
            for position,height,is_empty,allocation in self.compile_allocations(self.racks[j]):
                if is_empty:
                    style="empty"
                elif allocation.reserved:
                    style="reserved"
                else:
                    style="occupied"
                if allocation:
                    t=allocation.to_html()
                else:
                    t=""
                if height==1:
                    rsm[position][j*2]={"class":style,"text":t}
                else:
                    rsm[position][j*2]={"class":style,"text":t,"rowspan":height}
                    for i in range(position-1,position-height,-1):
                        rsm[i][j*2]=None
        # Build rack labels row
        # Render rack titles
        rack_labels=["<tr>"]
        for r in self.racks:
            if r.id:
                rack_labels+=["<td colspan='2' class='racklabel'>%s</td>"%escape(r.id)]
            else:
                rack_labels+=["<td colspan='2' class='racklabel'></td>"]
        rack_labels+=["</tr>"]
        # Render the matrix
        out=["<table class='rackset'>"]
        if self.id:
            out+=["<caption>%s</caption>"%escape(self.id)]
        if self.label in ["both","top"]:
            out+=rack_labels
        for i in range(self.height,0,-1):
            out+=["<tr>"]
            for j in range(len(self.racks)*2):
                v=rsm[i][j]
                if v:
                    td="<td "
                    for attr in ["colspan","rowspan","class"]:
                        if attr in v:
                            td+="%s='%s' "%(attr,v[attr])
                    td+=">"
                    # Render allocation
                    if "text" in v and v["text"]:
                        td+=v["text"]
                    #
                    td+="</td>"
                    out+=[td]
            out+=["</tr>"]
        if self.label in ["both","bottom"]:
            out+=rack_labels
        out+=["</table>"]
        return u"\n".join(out)
##
## Rack Representation
##
class Rack(object):
    def __init__(self,rackset,id,height):
        self.rackset=rackset
        self.id=id
        self.height=height
        self.rackset.racks.append(self)
        self.allocations=[]
##
## Allocation representation
## Rendered to HTML by Rack.render_html
##
class Allocation(object):
    def __init__(self,rack,id,position,height,reserved=False,model="",asset_no="",serial="",hostname="",description="",href=""):
        self.rack=rack
        self.id=id
        self.position=position
        self.height=height
        self.reserved=reserved
        self.model=model
        self.asset_no=asset_no
        self.serial=serial
        self.hostname=hostname
        self.description=description
        self.href=href
        self.rack.allocations.append(self)
        self.slots=[]
    
    def __repr__(self):
        return "Allocation: id=%s position=%s height=%s"%(self.id,self.position,self.height)
    ##
    ## Render allocation's cell
    ##
    def to_html(self):
        r=[]
        if self.id:
            r+=["<b>%s</b>"%unroll_link(self.id)]
        if self.hostname:
            r+=["<u>%s</u>"%unroll_link(self.hostname)]
        if self.model:
            r+=[unroll_link(self.model)]
        if self.serial:
            r+=["S/N: %s"%unroll_link(self.serial)]
        if self.asset_no:
            r+=["#%s"%unroll_link(self.asset_no)]
        if self.description:
            r+=["<i>%s</i>"%unroll_link(self.description)]
        if self.href:
            r+=["<a href='%s'>Link...</a>"%self.href]
        if self.slots:
            rr=["<table border='1'>"]
            for s in self.slots:
                rr+=["<tr><td><b>%s</b></td>"%s.id]
                a=" class='reserved'" if s.reserved else ""
                rr+=["<td%s>%s</td></tr>"%(a,s.to_html())]
            rr+=["</table>"]
            r+=["".join(rr)]
        return "<br/>".join(r)
##
##
##
class Slot(object):
    def __init__(self,allocation,id=None,model="",hostname="",description="",reserved=False,asset_no="",serial="",href=""):
        self.allocation=allocation
        self.id=id
        self.model=model
        self.hostname=hostname
        self.description=description
        self.reserved=reserved
        self.asset_no=asset_no
        self.serial=serial
        self.href=href
        self.allocation.slots.append(self)
    
    def to_html(self):
        r=[]
        if self.hostname:
            r+=["<u>%s</u>"%unroll_link(self.hostname)]
        if self.model:
            r+=[unroll_link(self.model)]
        if self.serial:
            r+=["S/N: %s"%unroll_link(self.serial)]
        if self.asset_no:
            r+=["#%s"%unroll_link(self.asset_no)]
        if self.description:
            r+=["<i>%s</i>"%unroll_link(self.description)]
        if self.href:
            r+=["<a href='%s'>Link...</a>"%self.href]
        return "<br/>".join(r)
##
## Expat parser to render simple XML grammar
## Tag hirrarchy:
##     rackset attrs: id
##       `-> rack attrs: id, height
##              `-> allocation attrs: id, position, height, reserved, model, hostname, description, assetno, href, serial
##                    `-> slot attrs: id, model, hostname, description, reserved, assetno, href, serial
##
class XMLParser(object):
    def __init__(self,text):
        self.parser=xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler=self.start_element
        self.parser.EndElementHandler=self.end_element
        self.parser.CharacterDataHandler =self.char_data
        self.rackset=None
        self.last_rack=None
        self.last_allocation=None
        if not text.startswith("<?"):
            text=u"<?xml version='1.0' encoding='utf-8' ?>\n"+text # Add missed XML prolog
        self.parser.Parse(unicode(text).encode("utf-8"))
    ##
    ## Called on tag opening
    ##
    def start_element(self,name,attrs):
        if name=="rackset":
            self.rackset=RackSet(id=attrs.get("id",None),label=attrs.get("label",None))
        elif name=="rack":
            height=attrs.get("height","1U").upper()
            if height.endswith("U"):
                height=height[:-1]
            self.last_rack=Rack(self.rackset,id=attrs.get("id",None),height=int(height))
        elif name=="allocation":
            height=attrs.get("height","1U").upper()
            if height.endswith("U"):
                height=height[:-1]
            self.last_allocation=Allocation(self.last_rack,
                id=attrs.get("id",None),
                height=int(height),
                position=int(attrs.get("position",0)),
                reserved=int(attrs.get("reserved",0)),
                model=attrs.get("model",""),
                hostname=attrs.get("hostname",""),
                asset_no=attrs.get("assetno",""),
                serial=attrs.get("serial",""),
                href=attrs.get("href",""),
                description=attrs.get("description","")
                )
        elif name=="slot":
            Slot(self.last_allocation,
                id=attrs.get("id",None),
                model=attrs.get("model",""),
                hostname=attrs.get("hostname",""),
                description=attrs.get("description",""),
                asset_no=attrs.get("assetno",""),
                serial=attrs.get("serial",""),
                href=attrs.get("href",""),
                reserved=int(attrs.get("reserved",0)))
    def end_element(self,name): pass
    def char_data(self,name): pass

##
## rack macro. XML contained in macro text
##
class Macro(MacroBase):
    name="rack"
    @classmethod
    def handle(cls,args,text):
        parser=XMLParser(text)
        return unicode(parser.rackset.render_html())
