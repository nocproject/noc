# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.vc.models import *

class Migration:
    def forwards(self):
        VCType = db.mock_model(model_name='VCType', db_table='vc_vctype', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.add_column("vc_vcdomain","type", models.ForeignKey(VCType,verbose_name="type",blank=True,null=True))
        # VLAN Type
        vlan_type,=db.execute("SELECT id FROM vc_vctype WHERE name=%s",["802.1Q VLAN"])[0]
        # Fill vc_domain.type_id
        for vc_domain_id,domain_name in db.execute("SELECT id,name FROM vc_vcdomain"):
            count,=db.execute("SELECT COUNT(DISTINCT type_id) FROM vc_vc WHERE vc_domain_id=%s",[vc_domain_id])[0]
            if count==0: # Set default type for empty domains
                db.execute("UPDATE vc_vcdomain SET type_id=%s WHERE id=%s",[vlan_type,vc_domain_id])
            elif count==1:
                type_id,=db.execute("SELECT DISTINCT type_id FROM vc_vc WHERE vc_domain_id=%s",[vc_domain_id])[0]
                db.execute("UPDATE vc_vcdomain SET type_id=%s WHERE id=%s",[type_id,vc_domain_id])
            else: # Crazy combination
                types=db.execute("SELECT DISTINCT type_id FROM vc_vc WHERE vc_domain_id=%s",[vc_domain_id])
                t0=types.pop(0)[0]
                db.execute("UPDATE vc_vcdomain SET type_id=%s WHERE id=%s",[t0,vc_domain_id])
                i=0
                for t, in types:
                    # Create stub
                    n=domain_name+" %d"%i
                    db.execute("INSERT INTO vc_vcdomain(name,type_id,description) VALUES(%s,%s,%s)",[n,t,"Collision Resolved"])
                    d_id,=db.execute("SELECT id FROM vc_vcdomain WHERE name=%s",[n])[0]
                    # Fix collisions
                    db.execute("UPDATE vc_vc SET vc_domain_id=%s WHERE vc_domain_id=%s AND type_id=%s",[d_id,vc_domain_id,t])
    
    def backwards(self):
        VCType = db.mock_model(model_name='VCType', db_table='vc_vctype', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        db.add_column("vc_vc","type", models.ForeignKey(VCType,verbose_name="type",blank=True,null=True))
        for vc_domain_id,type_id in db.execute("SELECT id,type_id FROM vc_vcdomain"):
            db.execute("UPDATE vc_vc SET type_id=%s WHERE vc_domain_id=%s",[type_id,vc_domain_id])
        db.drop_column("vc_vcdomain","type_id")