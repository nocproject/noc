#!/usr/bin/env python
#
# Looking Glass Daemon
#
import sys,psycopg2,asyncore,re,socket,os,logging,signal

#
rx_url=re.compile("^(?P<scheme>[^:]+)://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^/]+)(/|$)")
##
## Supervisor:
##
class Supervisor(object):
    def __init__(self):
        logging.info("Starting supervisor")
        logging.info("Setting signal handlers")
        signal.signal(signal.SIGCHLD,self.sig_chld)
        logging.info("Connecting to database")
        self.connect=psycopg2.connect("user=dima dbname=noc")
        self.connect.set_isolation_level(0)
        self.query_checker=QueryChecker(self)
        self.cursor=self.get_cursor()
        self.children={}
        self.cleanup()
        logging.info("Supervisor is ready")
        
    def get_cursor(self):
        logging.debug("Creating cursor")
        return self.connect.cursor()
        
    def cleanup(self):
        logging.debug("Cleaning up")
        self.cursor.execute("BEGIN");
        self.cursor.execute("DELETE FROM peer_lgquery WHERE status IN ('n','p')")
        self.cursor.execute("DELETE FROM peer_lgquery WHERE time<('now'::timestamp-'1h'::interval)")
        self.cursor.execute("COMMIT");
        
    def run(self):
        while 1:
            asyncore.loop(timeout=1,count=1)
            
    def start_lookup(self,id,peering_point_id,query_type_id,query):
        self.cursor.execute("BEGIN")
        self.cursor.execute("SELECT ppt.name,pp.lg_rcmd,c.command "\
            +"FROM peer_lgquerycommand c JOIN peer_peeringpointtype ppt ON (c.peering_point_type_id=ppt.id) "\
            +"JOIN peer_peeringpoint pp ON (pp.type_id=ppt.id) "\
            +"WHERE pp.id=%d AND c.query_type_id=%d"%(peering_point_id,query_type_id))
        r=self.cursor.fetchall()
        if len(r)==0:
            self.query_error("Query type is not supported")
        else:
            ppt,rcmd,command=r[0]
            if "%(query)s" in command:
                command=command%{"query":query}
            self.rcmd(ppt,id,rcmd,command)
        self.cursor.execute("COMMIT")
        
    def query_error(self,id,msg):
        logging.debug("Query error: query_id=%d %s"%(id,msg))
        self.cursor.execute("BEGIN")
        self.cursor.execute("UPDATE peer_lgquery SET status='f',out='%s' WHERE id=%d"%(msg.replace("'","''"),id))
        self.cursor.execute("END")
        
    def rcmd(self,peeting_point_type,id,rcmd,command):
        logging.debug("RCMD: %s"%command)
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
        self.children[id]=ACCESS_SCHEME[scheme](self,STREAM_PARSERS[peeting_point_type],id,host,user,password,command)
        
    def append_output(self,id,out,status="p"):
        logging.debug("Writing output: id=%d status=%s out=%s"%(id,status,out.replace("\n","\\n")))
        self.cursor.execute("BEGIN")
        self.cursor.execute("UPDATE peer_lgquery SET status='%s',out=out||'%s' WHERE id=%d"%(status.replace("'","''"),
            out.replace("'","''"),id))
        self.cursor.execute("END")
        
    def sig_chld(self,signum,frame):
        logging.debug("SIGCHLD caught")
        pid,status=os.waitpid(-1,os.WNOHANG)
        logging.debug("Process PID=%d is terminated with code %d"%(pid,status))

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
## Stream Parsers
##
class StreamParser(object):
    pattern_username="[Uu]sername:"
    pattern_password="[Pp]assword:"
    pattern_prompt=r"^\S*[>#]"
    startup_commands=[]
    logout_commands=["exit"]
    
class IOSParser(StreamParser): pass

class JUNOSParser(StreamParser):
    pattern_prompt="^({master}\n)?\S*>"

STREAM_PARSERS={
    "IOS"   : IOSParser,
    "JUNOS" : JUNOSParser,
}

##
##
##
class SocketHandler(asyncore.dispatcher):
    def __init__(self,supervisor,parser,id,host,user,password,command):
        asyncore.dispatcher.__init__(self)
        self.supervisor=supervisor
        self.parser=parser
        self.id=id
        self.host=host
        self.user=user
        self.password=password
        self.command=command
        self.out_buffer=""
        self.in_buffer=""
        self.to_write_result=False
        self.expect=None
        self.prepare_socket()
        self.startup_commands=self.parser.startup_commands[:]
        self.logout_commands=self.parser.logout_commands[:]
        self.set_expect(
            [
                (self.parser.pattern_username,self.x_username),
                (self.parser.pattern_password,self.x_password),
            ])
    def prepare_socket(self):
        raise Exception,"No socket created"
        
    def set_expect(self,v=None):
        if v:
            r=[]
            for rx,handler in v:
                r.append((re.compile(rx,re.DOTALL|re.MULTILINE),handler))
            self.expect=r
        else:
            self.expect=None
            
    def set_result_output(self,v):
        if v:
            logging.debug("Starting to write result")
        else:
            logging.debug("Stopping to write result")
        self.to_write_result=v
            
    def write(self,txt):
        logging.debug("Writing: %s"%txt.replace("\n","\\n"))
        self.out_buffer+=txt
        
    def write_result(self,r):
        if self.to_write_result:
            logging.debug("Writting result: %s"%r.replace("\n","\\n"))
            self.supervisor.append_output(self.id,r)
    
    def handle_read(self):
        d=self.recv(8192)
        d=d.replace("\r","")
        logging.debug("Received: %s"%d.replace("\n","\\n"))
        self.in_buffer+=d
        if self.expect:
            for rx,handler in self.expect:
                match=rx.search(self.in_buffer)
                if match:
                    self.write_result(self.in_buffer[:match.start(0)])
                    self.in_buffer=self.in_buffer[match.end(0):]
                    logging.debug("FSM transition: %s"%(str(handler)))
                    self.set_expect(handler(match))
                    break
        
    def handle_write(self):
        sent=self.send(self.out_buffer)
        self.out_buffer=self.out_buffer[sent:]
        
    def writable(self):
        return len(self.out_buffer)>0

    def handle_connect(self):
        pass
        
    def handle_close(self):
        logging.debug("Handle close")
        self.close()
        self.write_result(self.in_buffer)
        self.supervisor.append_output(self.id,"",status="c")
        
    def x_username(self,match):
        self.write(self.user+"\n")
        return [(self.parser.pattern_password,self.x_password)]

    def x_password(self,match):
        self.write(self.password+"\n")
        if len(self.startup_commands):
            return [(self.parser.pattern_prompt,self.x_startup_prompt)]
        else:
            return [(self.parser.pattern_prompt,self.x_prompt)]
            
    def x_startup_prompt(self,match):
        sc=self.startup_commands.pop(0)
        self.write(sc+"\n")
        if len(self.startup_commands):
            return [(self.parser.pattern_prompt,self.x_startup_prompt)]
        else:
            return [(self.parser.pattern_prompt,self.x_prompt)]
    
    def x_logout_prompt(self,match):
        self.set_result_output(False)
        lc=self.logout_commands.pop(0)
        self.write(lc+"\n")
        return [(self.parser.pattern_prompt,self.x_logout_prompt)]

    def x_prompt(self,match):
        self.write(self.command+"\n")
        self.set_result_output(True)
        return [(self.parser.pattern_prompt,self.x_logout_prompt)]
##
##
##
class TelnetHandler(SocketHandler):
    def prepare_socket(self):
        logging.debug("TelnetHandler connecting %s"%self.host)
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connect((self.host,23))
#
#
#
class SSHHandler(SocketHandler):
    def prepare_socket(self):
        logging.debug("SSHHandler connecting %s"%self.host)
        pid,fd=os.forkpty()
        if pid==0:
            os.execv("/usr/bin/ssh",["/usr/bin/ssh","-l",self.user,self.host])
        else:
            self.set_socket(asyncore.file_wrapper(fd))

ACCESS_SCHEME={
    "telnet" : TelnetHandler,
    "ssh"    : SSHHandler,
}
#

def usage(): pass

def main():
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')
    logging.info("Starting LGD")
    supervisor=Supervisor()
    supervisor.run()
    
if __name__ == '__main__':
	main()

