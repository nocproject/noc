
from south.db import db
from noc.vc.models import *

vc_checks={
    "q": ("802.1Q VLAN",        1, (1,4095),     None),
    "Q": ("802.1ad Q-in-Q",     2, (1,4095),     (1,4095)),
    "D": ("FR DLCI",            1, (16,991),     None),
    "M": ("MPLS",               1, (16,1048575), (16,1048575)),
    "A": ("ATM VCI/VPI",        1, (0,65535),    (0,4095)),
    "X": ("X.25 group/channel", 2, (0,15),       (0,255)),
}

class Migration:
    
    def forwards(self):
        # Save old VCs
        vc_data=db.execute("SELECT vc_domain_id,type,l1,l2,description FROM vc_vc ORDER by id")
        # Delete old VC table
        db.delete_table("vc_vc")
        # Model 'VCType'
        db.create_table('vc_vctype', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField("Name",max_length=32,unique=True)),
            ('min_labels', models.IntegerField("Min. Labels",default=1)),
            ('label1_min', models.IntegerField("Label1 min")),
            ('label1_max', models.IntegerField("Label1 max")),
            ('label2_min', models.IntegerField("Label2 min",null=True,blank=True)),
            ('label2_max', models.IntegerField("Label2 max",null=True,blank=True))
        ))
        
        # Mock Models
        VCDomain = db.mock_model(model_name='VCDomain', db_table='vc_vcdomain', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        VCType = db.mock_model(model_name='VCType', db_table='vc_vctype', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
        # Model 'VC'
        db.create_table('vc_vc', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('vc_domain', models.ForeignKey(VCDomain,verbose_name="VC Domain")),
            ('type', models.ForeignKey(VCType,verbose_name="type")),
            ('l1', models.IntegerField("Label 1")),
            ('l2', models.IntegerField("Label 2",default=0)),
            ('description', models.CharField("Description",max_length=256))
        ))
        db.create_index('vc_vc', ['vc_domain_id','type_id','l1','l2'], unique=True, db_tablespace='')
        
        db.send_create_signal('vc', ['VCType','VC'])
        # Fill in VC types
        vc_map={} # letter -> id
        for vt,d in vc_checks.items():
            name,min_labels,l1,l2=d
            if l2 is None:
                l2=(0,0)
            db.execute("INSERT INTO vc_vctype(name,min_labels,label1_min,label1_max,label2_min,label2_max) VALUES(%s,%s,%s,%s,%s,%s)",
                [name,min_labels,l1[0],l1[1],l2[0],l2[1]])
            vct_id=db.execute("SELECT id FROM vc_vctype WHERE name=%s",[name])[0][0]
            vc_map[vt]=vct_id
        # Return saved VC data
        for vc_domain_id,type,l1,l2,description in vc_data:
            db.execute("INSERT INTO vc_vc(vc_domain_id,type_id,l1,l2,description) VALUES(%s,%s,%s,%s,%s)",
                [vc_domain_id,vc_map[type],l1,l2,description])
    
    def backwards(self):
        db.delete_table('vc_vc')
        db.delete_table('vc_vctype')
        
