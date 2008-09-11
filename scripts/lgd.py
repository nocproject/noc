#!/usr/bin/env python
#
# Looking Glass Daemon
#
import sys,psycopg2,asyncore,re,socket,os

#
rx_url=re.compile("^(?P<scheme>[^:]+)://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^/]+)(/|$)")
##
## Supervisor:
##
class Supervisor(object):
    def __init__(self):
        self.connect=psycopg2.connect("user=dima dbname=noc")
        self.connect.set_isolation_level(0)
        self.query_checker=QueryChecker(self)
        self.cursor=self.get_cursor()
        self.children={}
        self.cleanup()
        
    def get_cursor(self):
        return self.connect.cursor()
        
    def cleanup(self):
        self.cursor.execute("BEGIN");
        self.cursor.execute("DELETE FROM peer_lgquery WHERE status IN ('n','p')")
        self.cursor.execute("COMMIT");
        
    def run(self):
        while 1:
            asyncore.loop(timeout=1,count=1)
            
    def start_lookup(self,id,peering_point_id,query_type_id,query):
        self.cursor.execute("BEGIN")
        self.cursor.execute("SELECT pp.lg_rcmd,c.command "\
            +"FROM peer_lgquerycommand c JOIN peer_peeringpointtype ppt ON (c.peering_point_type_id=ppt.id) "\
            +"JOIN peer_peeringpoint pp ON (pp.type_id=ppt.id) "\
            +"WHERE pp.id=%d AND c.query_type_id=%d"%(peering_point_id,query_type_id))
        r=self.cursor.fetchall()
        if len(r)==0:
            self.query_error("Query type is not supported")
        else:
            rcmd,command=r[0]
            if "%(query)s" in command:
                command=command%{"query":query}
            self.rcmd(id,rcmd,command)
        self.cursor.execute("COMMIT")
        
    def query_error(self,id,msg):
        self.cursor.execute("BEGIN")
        self.cursor.execute("UPDATE peer_lgquery SET status='f',out='%s' WHERE id=%d"%(msg.replace("'","''"),id))
        self.cursor.execute("END")
        
    def rcmd(self,id,rcmd,command):
        match=rx_url.match(rcmd)
        if not match:
            self.query_error(id,"Invalid RCMD")
            return
        scheme=match.group("scheme")
        user=match.group("user")
        password=match.group("password")
        host=match.group("host")
        if scheme not in ACCESS_SCHEME:
            self.query_error("Unsupported access scheme: %s"%scheme)
            return
        self.children[id]=ACCESS_SCHEME[scheme](self,id,host,user,password,command)
        
    def append_output(self,id,out,status="p"):
        self.cursor.execute("BEGIN")
        self.cursor.execute("UPDATE peer_lgquery SET status='%s',out=out||'%s' WHERE id=%d"%(status.replace("'","''"),
            out.replace("'","''"),id))
        self.cursor.execute("END")

##
## QueryChecker
##
class QueryChecker(asyncore.dispatcher):
    def __init__(self,supervisor):
        asyncore.dispatcher.__init__(self)
        self.supervisor=supervisor
        self.cursor=self.supervisor.get_cursor()
        # Mark all incomplete queries as failed
        self.cursor.execute("BEGIN")
        self.cursor.execute("UPDATE peer_lgquery SET status='f',out=out||'...Connection reset' WHERE status IN ('n','p')")
        self.cursor.execute("COMMIT")
        self.cursor.execute("LISTEN lg_new_query")
        self.set_socket(self.cursor)
        
    def handle_read(self):
        while self.cursor.isready() and len(self.cursor.connection.notifies)>0:
            pid,event=self.cursor.connection.notifies.pop()
            self.cursor.execute("SELECT id,peering_point_id,query_type_id,query FROM peer_lgquery WHERE status='n'")
            for id,peering_point_id,query_type_id,query in self.cursor.fetchall():
                self.supervisor.start_lookup(id,peering_point_id,query_type_id,query)

    def writable(self):
        return False

    def handle_connect(self):
        pass
##
##
##
class SocketHandler(asyncore.dispatcher):
    def __init__(self,supervisor,id,host,user,password,command):
        asyncore.dispatcher.__init__(self)
        self.supervisor=supervisor
        self.id=id
        self.host=host
        self.user=user
        self.password=password
        self.command=command
        self.out_buffer=""
        self.in_buffer=""
        self.result=""
        self.expect=None
        self.prepare_socket()
        
    def prepare_socket(self):
        pass
        
    def set_expect(self,v=None):
        if v:
            r=[]
            for rx,handler in v:
                r.append((re.compile(rx),handler))
            self.expect=r
        else:
            self.expect=None
            
    def write(self,txt):
        self.out_buffer+=txt
    
    def handle_read(self):
        self.in_buffer+=self.recv(8192)
        if self.expect:
            for rx,handler in self.expect:
                match=rx.search(self.in_buffer)
                if match:
                    self.set_expect(handler(match))
                    self.in_buffer=self.in_buffer[match.endpos:]
        
    def handle_write(self):
        sent=self.send(self.out_buffer)
        self.out_buffer=self.out_buffer[sent:]
        
    def writable(self):
        return len(self.out_buffer)>0

    def handle_connect(self):
        pass
        
    def handle_close(self):
        self.close()
        self.supervisor.append_output(self.id,self.result,status="c")

##
##
##
class TelnetHandler(SocketHandler):
    def prepare_socket(self):
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connect((self.host,23))
        self.set_expect([("Username:",self.x_username)])
        
    # Expect handlers
    def x_username(self,match):
        self.write(self.user+"\n")
        return [("Password:",self.x_password)]
        
    def x_password(self,match):
        self.write(self.password+"\n")
        return [("[>#]",self.x_prompt)]
        
    def x_prompt(self,match):
        self.write(self.command+"\n")
        return [("[>#]",self.x_end_prompt)]
        
    def x_end_prompt(self,match):
        self.result+=self.in_buffer
        self.write("exit"+"\n")
        return []
#
#
#
class SSHHandler(SocketHandler):
    def prepare_socket(self):
        pid,fd=os.forkpty()
        if pid==0:
            os.execv("/usr/bin/ssh",["/usr/bin/ssh","-l",self.user,self.host,self.command])
        else:
            self.set_socket(asyncore.file_wrapper(fd))
            self.set_expect([("password:",self.x_password)])
            
    def x_password(self,match):
        self.write(self.password+"\n")
        return [("[>#]",self.x_prompt)]
        
    def x_prompt(self,match):
        self.write(self.command+"\n")
        return [("[>#]",self.x_end_prompt)]
        
    def x_end_prompt(self,match):
        self.result+=self.in_buffer
        print "<<<<",self.result,">>>>"
        self.write("exit"+"\n")
        return []
            
ACCESS_SCHEME={
    "telnet" : TelnetHandler,
    "ssh"    : SSHHandler,
}
#

def usage(): pass

def main():
    supervisor=Supervisor()
    supervisor.run()
    
if __name__ == '__main__':
	main()

