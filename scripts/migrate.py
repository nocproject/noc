#!/usr/bin/env python
import psycopg2

TMP="/tmp/dmove.tmp"
DBOLD="oldnoc"
DBNEW="noc"

class Table(object):
    old_name=None
    new_name=None
    old_fields=None
    new_fields=None
    additional_columns=None
    additional_values=None
    def __init__(self,old_name=None,new_name=None,old_fields=None,new_fields=None,additional_columns=None,additional_values=None):
        if old_name:
            self.old_name=old_name
        if new_name:
            self.new_name=new_name
        if old_fields:
            self.old_fields=old_fields
        if new_fields:
            self.new_fields=new_fields
        if additional_columns:
            self.additional_columns=additional_columns
        if additional_values:
            self.additional_values=additional_values
        if self.new_name is None:
            self.new_name=self.old_name
        if self.new_fields is None:
            self.new_fields=self.old_fields
        if len(self.old_fields)!=len(self.new_fields):
            raise Exception,"Fields mismatch"
            
    def clean_table(self,cnew):
        print "Cleaning: %s"%self.new_name
        cnew.execute("DELETE FROM %s"%self.new_name)
    
    def move_table(self,cold,cnew):
        print "Move: %s -> %s"%(self.old_name,self.new_name)
        cold.execute("COPY %s (%s) TO '%s' CSV"%(self.old_name,",".join(self.old_fields),TMP))
        if self.additional_columns:
            f=open(TMP)
            data=f.read().split("\n")
            f.close()
            ndata=[]
            suffix=","+",".join(self.additional_values)
            for d in data:
                if d=="":
                    continue
                d+=suffix
                ndata.append(d)
            f=open(TMP+"a","w")
            f.write("\n".join(ndata))
            f.close()
            cnew.execute("COPY %s (%s) FROM '%s' CSV"%(self.new_name,",".join(self.new_fields+self.additional_columns),TMP+"a"))
        else:
            cnew.execute("COPY %s (%s) FROM '%s' CSV"%(self.new_name,",".join(self.new_fields),TMP))
        seq="%s_%s_seq"%(self.new_name,self.new_fields[0])
        cold.execute("SELECT MAX(%s)+1 FROM %s"%(self.old_fields[0],self.old_name))
        cnew.execute("SELECT SETVAL('%s',%d)"%(seq,cold.fetchall()[0][0]))
        
class TableNew(Table):
    def __init__(self,new_name,fields,values):
        self.new_name=new_name
        self.new_fields=fields
        self.values=values
        
    def move_table(self,cold,cnew):
        print "Creating: %s"%self.new_name
        f=open(TMP+"a","w")
        f.write(",".join(self.values))
        f.close()
        cnew.execute("COPY %s (%s) FROM '%s' CSV"%(self.new_name,",".join(self.new_fields),TMP+"a"))
        

def execute_script(cold,cnew,script):
    script.reverse()
    for t in script:
        t.clean_table(cnew)
    script.reverse()
    for t in script:
        t.move_table(cold,cnew)
    
    
SCRIPT=[
    Table(old_name="auth_user",old_fields=["id","username","first_name","last_name","email","password","is_staff",
        "is_active","is_superuser","last_login","date_joined"]),
    Table(old_name="auth_group",old_fields=["id","name"]),
    Table(old_name="auth_user_groups",old_fields=["id","user_id","group_id"]),
    # ASN
    Table(old_name="an_lir",new_name="asn_lir",old_fields=["id","name"]),
    Table(old_name="an_as",new_name="asn_as",old_fields=["id","lir_id","asn","description"]),
    # IP
    TableNew("ip_vrfgroup",["id","name","unique_addresses"],["1","Effortel","t"]),
    Table(old_name="an_vrf",new_name="ip_vrf",old_fields=["id","name","rd"],additional_columns=["vrf_group_id"],additional_values=["1"]),
    Table(old_name="an_ipv4block",new_name="ip_ipv4block",old_fields=["id","description","prefix","vrf_id","asn_id","modified_by_id","last_modified"]),
    Table(old_name="an_ipv4address",new_name="ip_ipv4address",old_fields=["id","vrf_id","fqdn","ip","description","modified_by_id",
        "last_modified"]),
    # DNS
    Table(old_name="an_dnszoneprofile",new_name="dns_dnszoneprofile",old_fields=["id","name","zone_transfer_acl","zone_ns_list",
        "zone_soa","zone_contact","zone_refresh","zone_retry","zone_expire","zone_ttl"]),
    Table(old_name="an_dnszone",new_name="dns_dnszone",old_fields=["id","name","description","is_auto_generated","serial","profile_id"]),
    ]
    
if __name__=="__main__":
    cnold=psycopg2.connect("dbname=%s"%DBOLD)
    cnnew=psycopg2.connect("dbname=%s"%DBNEW)
    cold=cnold.cursor()
    cnew=cnnew.cursor()
    cnew.execute("BEGIN")
    execute_script(cold,cnew,SCRIPT)
    cnew.execute("COMMIT")