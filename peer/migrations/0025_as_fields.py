# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.peer.models import *
import re

rx_remarks=re.compile(r"^remarks:\s*")

class Migration:
    
    def forwards(self, orm):
        RIR = db.mock_model(model_name='RIR', db_table='peer_rir', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        AS = db.mock_model(model_name='AS', db_table='peer_as', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        Person = db.mock_model(model_name='Person', db_table='peer_person', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        Maintainer = db.mock_model(model_name='Maintainer', db_table='peer_maintainer', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        db.create_table("peer_organisation", (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('organisation', models.CharField("Organisation",max_length=128,unique=True)),
            ('org_name', models.CharField("Org. Name",max_length=128)),
            ('org_type', models.CharField("Org. Type",max_length=64,choices=[("LIR","LIR")])),
            ('address', models.TextField("Address")),
            ('mnt_ref', models.ForeignKey(Maintainer,verbose_name="Mnt. Ref")),
        ))
        
        Organisation = db.mock_model(model_name='Organisation', db_table='peer_organisation', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        db.add_column("peer_as","rir",models.ForeignKey(RIR,null=True,blank=True))
        db.add_column("peer_as", "organisation", models.ForeignKey(Organisation,null=True,blank=True))
        db.add_column("peer_as",'header_remarks', models.TextField("Header Remarks", null=True, blank=True))
        db.add_column("peer_as",'footer_remarks', models.TextField("Footer Remarks", null=True, blank=True))

        # Adding ManyToManyField 'AS.maintainers'
        db.create_table('peer_as_maintainers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('as', models.ForeignKey(AS, null=False)),
            ('maintainer', models.ForeignKey(Maintainer, null=False))
        ))
        
        # Adding ManyToManyField 'AS.tech_contacts'
        db.create_table('peer_as_tech_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('as', models.ForeignKey(AS, null=False)),
            ('person', models.ForeignKey(Person, null=False))
        ))
        
        # Adding ManyToManyField 'AS.routes_maintainers'
        db.create_table('peer_as_routes_maintainers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('as', models.ForeignKey(AS, null=False)),
            ('maintainer', models.ForeignKey(Maintainer, null=False))
        ))
        
        # Adding ManyToManyField 'AS.administrative_contacts'
        db.create_table('peer_as_administrative_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('as', models.ForeignKey(AS, null=False)),
            ('person', models.ForeignKey(Person, null=False))
        ))
        
        # Fill out RIR
        ripe_id=db.execute("SELECT id FROM peer_rir WHERE name=%s",["RIPE NCC"])[0]
        db.execute("UPDATE peer_as SET rir_id=%s",[ripe_id])
        # Fill out organisation
        mnt_id=db.execute("SELECT id FROM peer_maintainer LIMIT 1")[0][0]
        db.execute("INSERT INTO peer_organisation(organisation,org_name,org_type,address,mnt_ref_id) VALUES(%s,%s,%s,%s,%s)",
            ["ORG-DEFAULT","Default Organisation","LIR","Anywhere",mnt_id])
        org_id=db.execute("SELECT id FROM peer_organisation LIMIT 1")[0][0]
        db.execute("UPDATE peer_as SET organisation_id=%s",[org_id])
        # Migrate headers and footers
        for id,rpsl_header,rpsl_footer in db.execute("SELECT id,rpsl_header,rpsl_footer FROM peer_as"):
            header_remarks=rpsl_header
            if header_remarks:
                header_remarks="\n".join([rx_remarks.sub("",x) for x in rpsl_header.split("\n")])
            footer_remarks=rpsl_footer
            if footer_remarks:
                footer_remarks="\n".join([rx_remarks.sub("",x) for x in rpsl_footer.split("\n")])
            db.execute("UPDATE peer_as SET header_remarks=%s,footer_remarks=%s WHERE id=%s",[header_remarks,footer_remarks,id])
        db.execute("COMMIT")
        # 
        db.delete_column("peer_as","maintainer_id")
        db.delete_column("peer_as","routes_maintainer_id")
        db.delete_column("peer_as","rpsl_header")
        db.delete_column("peer_as","rpsl_footer")        
        db.execute("ALTER TABLE peer_as ALTER rir_id SET NOT NULL")
        db.execute("ALTER TABLE peer_as ALTER organisation_id SET NOT NULL")
    
    def backwards(self, orm):
        # Dropping ManyToManyField 'AS.maintainers'
        db.delete_table('peer_as_maintainers')
        
        # Dropping ManyToManyField 'AS.tech_contacts'
        db.delete_table('peer_as_tech_contacts')
        
        # Dropping ManyToManyField 'AS.routes_maintainers'
        db.delete_table('peer_as_routes_maintainers')
        
        # Dropping ManyToManyField 'AS.administrative_contacts'
        db.delete_table('peer_as_administrative_contacts')

        db.delete_column("peer_as","rir")
        db.delete_column("peer_as",'header_remarks')
        db.delete_column("peer_as",'footer_remarks')
