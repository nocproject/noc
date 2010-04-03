# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Embedded TFTP Server
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.lib.nbsocket import ListenUDPSocket
import struct
##
## TFTP Server
##
class TFTPServer(ListenUDPSocket):
    # Opcodes
    RRQ=1
    WRQ=2
    DATA=3
    ACK=4
    ERROR=5
    # Error codes
    ERR_UNDEF=0      # Not defined, see error message (if any).
    ERR_NOT_FOUND=1  #File not found.
    ERR_ACCESS=2     # Access violation.
    ERR_FULL=3       # Disk full or allocation exceeded.
    ERR_ILLEGAL=4    # Illegal TFTP operation.
    ERR_UNK_ID=5     # Unknown transfer ID.
    ERR_AEXISTS=6    # File already exists.
    ERR_NOUSER=7     # No such user.
    def __init__(self,factory,address,server_hub):
        super(TFTPServer,self).__init__(factory,address,69)
        self.active_transfers={} # (addres,port) -> url
    
    def on_read(self,data,address,port):
        # Parse data
        if len(data)<2:
            self.send_error(address,port,self.ERR_ILLEGAL,"Illegal TFTP operation")
            return
        code=struct.unpack("!H",data[:2])
        if code<self.RRQ or code>self.ERROR:
            self.send_error(address,port,self.ERR_ILLEGAL,"Illegal TFTP operation")
            return
        data=data[2:]
        if code in [self.RRQ,self.WRQ]:
            try:
                index=data.index("\x00")
                filename=data[:index]
                data=data[index+1:]
                index=data.index("\x00")
                mode=data[:index]
            except ValueError:
                self.send_error(address,port,self.ERR_ILLEGAL,"Illegal TFTP operation")
                return
            if code==self.RRQ:
                # Check data exists
                if not self.has_data(filename):
                    self.send_error(address,port,self.ERR_NOT_FOUND,"File %s is not found"%filename)
                    return
                self.start_transfer(self,filename,address,port)
                # Send first data packet
                self.send_data(address,port,0)
            elif code==self.WRQ:
                self.send_error(address,port,self.ERR_ILLEGAL,"WRQ is not implemented yet")
                return
        elif code==self.DATA:
            block_no,=struct.unpack("!H",data[:2])
            data=data[2:]
            self.send_error(address,port,self.ERR_ILLEGAL,"DATA is not implemented yet")
            return
        elif code==self.ACK:
            if len(data)!=2:
                self.send_error(address,port,self.ERR_ILLEGAL,"Invalid ACK")
                return
            block_no,=struct.unpack("!H",data[:2])
            if (address,port) not in self.active_transfers:
                self.send_error(address,port,self.ERR_UNK_ID,"Unknown TID")
                return
            self.send_data(address,port,block_no+1) # Send next packet
        elif code==self.ERROR:
            if len(data)<3:
                self.send_error(address,port,self.ERR_ILLEGAL,"Illegal TFTP operation")
                return
            error_code,=struct.unpack("!H",data[:2])
            data=data[2:]
            try:
                index=data.index("\x00")
                error_message=data[:index]
            except ValueError:
                self.send_error(address,port,self.ERR_ILLEGAL,"Illegal TFTP operation")
                return
            # <!> Do nothing yet
    ##
    ## Send error packet
    ##
    def send_error(self,address,port,code,message):
        pkt=struct.pack("!H!H",self.ERROR,code)
        pkt+=message+"\x00"
        self.sendto(pkt,(address,port))
    ##
    ## Send DATA packet
    ##
    def send_data(self,address,port,block_no):
        try:
            url=self.active_transfers[(address,port)]
        except:
            self.send_error(address,port,self.ERR_NOT_FOUND,"File not found")
            return
        data=self.dl_data[url][block_no*512:block_no*512+512]
        pkt=struck.pack("!H!H",self.DATA,block_no)
        pkt+=data
        self.sendto(pkt,(address,port))
    ##
    ## Start transfer
    ##
    def start_transfer(self,url,address,port):
        self.active_transfers[(address,port)]=url
    ##
    ## Stop transfer
    ##
    def stop_transfer(self,address,port):
        try:
            del self.active_transfers[(address,port)]
        except:
            pass