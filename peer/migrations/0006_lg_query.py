
from south.db import db
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        # Mock Models
        PeeringPoint = db.mock_model(model_name='PeeringPoint', db_table='peer_peeringpoint', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        LGQueryType = db.mock_model(model_name='LGQueryType', db_table='peer_lgquerytype', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'LGQuery'
        db.create_table('peer_lgquery', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('remote_addr', models.IPAddressField("REMOTE_ADDR")),
            ('query_id', models.IntegerField("Query ID")),
            ('time', models.DateTimeField("Time",auto_now_add=True,auto_now=True)),
            ('status', models.CharField("Status",max_length=1, choices=[("n","New"),("p","In Progress"),("f","Failure"),("c","Complete")],default="n")),
            ('peering_point', models.ForeignKey(PeeringPoint,verbose_name="Peering Point")),
            ('query_type', models.ForeignKey(LGQueryType,verbose_name="Query Type")),
            ('query', models.CharField("Query",max_length=128,null=True,blank=True)),
            ('out', models.TextField("Out",default=""))
        ))
        db.create_index('peer_lgquery', ['remote_addr','query_id'], unique=True, db_tablespace='')
        db.send_create_signal('peer', ['LGQuery'])
        from django.db import connection
        self.cursor=connection.cursor()
        self.sql(CREATE_F_PEER_LGQUERY_INSERT)
        self.sql(CREATE_T_PEER_LGQUERY_INSERT)
    
    def backwards(self):
        from django.db import connection
        self.cursor=connection.cursor()
        self.sql(DROP_T_PEER_LGQUERY_INSERT)
        self.sql(DROP_F_PEER_LGQUERY_INSERT)
        db.delete_table('peer_lgquery')
        
    def sql(self,q):
        print q
        self.cursor.execute(q)
        
CREATE_F_PEER_LGQUERY_INSERT="""
CREATE OR REPLACE
FUNCTION f_peer_lgquery_insert()
RETURNS TRIGGER
AS $$
BEGIN
    NOTIFY lg_new_query;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
"""

CREATE_T_PEER_LGQUERY_INSERT="""
CREATE TRIGGER t_peer_lgquery_insert
AFTER INSERT ON peer_lgquery
FOR EACH STATEMENT EXECUTE PROCEDURE f_peer_lgquery_insert();
"""

DROP_T_PEER_LGQUERY_INSERT="""
DROP TRIGGER IF EXISTS t_peer_lgquery_insert ON peer_lgquery;
"""

DROP_F_PEER_LGQUERY_INSERT="""
DROP FUNCTION f_peer_lgquery_insert();
"""