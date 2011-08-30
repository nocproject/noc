# encoding: utf-8
import datetime
from south.db import db
from django.db import models
from noc.lib.fields import AutoCompleteTagsField,CIDRField,INETField,MACField
from django.contrib.contenttypes.management import update_contenttypes
import noc.ip.models

class Migration:
    depends_on=(
        ("main", "0027_style"),
    )
    def forwards(self):
        AFI_CHOICES=[
            ("4", "IPv4"),
            ("6", "IPv6")
        ]
        # Style
        Style=db.mock_model(model_name='Style',db_table='main_style',db_tablespace='',pk_field_name='id',pk_field_type=models.AutoField)
        # VRF Group
        db.add_column("ip_vrfgroup","address_constraint",
            models.CharField("Address Constraint",max_length=1,
                choices=[("V","Addresses are unique per VRF"),("G","Addresses are unique per VRF Group")],default="V"))
        db.alter_column("ip_vrfgroup","description",models.TextField("Description",blank=True,null=True,default="V"))
        db.add_column("ip_vrfgroup","tags",AutoCompleteTagsField("Tags",null=True,blank=True))
        # VRF
        db.add_column("ip_vrf","is_active",models.BooleanField("Is Active",default=True))
        db.add_column("ip_vrf","afi_ipv4",models.BooleanField("IPv4",default=True))
        db.add_column("ip_vrf","afi_ipv6",models.BooleanField("IPv6",default=False))
        db.alter_column("ip_vrf","description",models.TextField("Description",blank=True,null=True,default="V"))
        db.add_column("ip_vrf","style",models.ForeignKey(Style,verbose_name="Style", blank=True, null=True))
        db.add_column("ip_vrf","allocated_till",models.DateField("Allocated till",null=True,blank=True))
        # Prefix
        VRF=db.mock_model(model_name='VRF',db_table='ip_vrf',db_tablespace='',pk_field_name='id',pk_field_type=models.AutoField)
        AS=db.mock_model(model_name='AS',db_table='peer_as',db_tablespace='',pk_field_name='id',pk_field_type=models.AutoField)
        VC=db.mock_model(model_name='VC',db_table='vc_vc',db_tablespace='',pk_field_name='id',pk_field_type=models.AutoField)
        ManagedObject=db.mock_model(model_name='ManagedObject',db_table='sa_managedobject',db_tablespace='',pk_field_name='id',pk_field_type=models.AutoField)
        Prefix=db.mock_model(model_name='Prefix',db_table='ip_prefix',db_tablespace='',pk_field_name='id',pk_field_type=models.AutoField)
        
        db.create_table('ip_prefix', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ("parent", models.ForeignKey(Prefix,related_name="children_set",verbose_name="Parent",null=True,blank=True)),
            ("vrf", models.ForeignKey(VRF,verbose_name="VRF")),
            ("afi", models.CharField("Address Family",max_length=1,choices=AFI_CHOICES)),
            ("prefix", CIDRField("Prefix")),
            ("asn", models.ForeignKey(AS,verbose_name="AS")),
            ("vc", models.ForeignKey(VC,verbose_name="VC",null=True,blank=True)),
            ("description", models.TextField("Description",blank=True,null=True)),
            ("tags", AutoCompleteTagsField("Tags",null=True,blank=True)),
            ("tt", models.IntegerField("TT",blank=True,null=True)),
            ('style', models.ForeignKey(Style,verbose_name="Style", blank=True, null=True)),
            ("allocated_till", models.DateField("Allocated till",null=True,blank=True))
        ))
        db.create_index('ip_prefix', ['vrf_id','afi','prefix'], unique=True, db_tablespace='')
        # Address
        db.create_table('ip_address', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ("prefix", models.ForeignKey(Prefix,verbose_name="Prefix")),
            ("vrf", models.ForeignKey(VRF,verbose_name="VRF")),
            ("afi", models.CharField("Address Family",max_length=1,choices=AFI_CHOICES)),
            ("address", INETField("Address")),
            ("fqdn", models.CharField("FQDN",max_length=255)),
            ("mac", MACField("MAC",null=True,blank=True)),
            ("auto_update_mac", models.BooleanField("Auto Update MAC",default=False)),
            ("managed_object", models.ForeignKey(ManagedObject,verbose_name="Managed Object",null=True,blank=True,related_name="address_set")),
            ("description", models.TextField("Description",blank=True,null=True)),
            ("tags", AutoCompleteTagsField("Tags",null=True,blank=True)),
            ("tt", models.IntegerField("TT",blank=True,null=True)),
            ('style', models.ForeignKey(Style,verbose_name="Style", blank=True, null=True)),
            ("allocated_till", models.DateField("Allocated till",null=True,blank=True)),
        ))
        db.create_index('ip_address', ['prefix_id','vrf_id','afi','address'], unique=True, db_tablespace='')
        # PrefixAccess
        User=db.mock_model(model_name='User',db_table='auth_user',db_tablespace='',pk_field_name='id',pk_field_type=models.AutoField)
        db.create_table('ip_prefixaccess',(
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ("user", models.ForeignKey(User,verbose_name="User")),
            ("vrf", models.ForeignKey(VRF,verbose_name="VRF")),
            ("afi", models.CharField("Address Family",max_length=1,choices=AFI_CHOICES)),
            ("prefix", CIDRField("Prefix")),
            ("can_view", models.BooleanField("Can View",default=False)),
            ("can_change", models.BooleanField("Can Change",default=False)),
        ))
        db.create_index('ip_prefixaccess', ['user_id','vrf_id','afi','prefix'], unique=True, db_tablespace='')
        # AddressRange
        db.create_table('ip_addressrange', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('name', models.CharField(_("Name"),max_length=64,unique=True)),
            ('is_active', models.BooleanField(_("Is Active"),default=True)),
            ("vrf", models.ForeignKey(VRF,verbose_name="VRF")),
            ("afi", models.CharField("Address Family",max_length=1,choices=AFI_CHOICES)),
            ("from_address", INETField("Address")),
            ("to_address", INETField("Address")),
            ("description", models.TextField("Description",blank=True,null=True)),
            ('is_locked', models.BooleanField(_("Is Active"),default=True)),
            ('action', models.CharField(_("FQDN Action"),max_length=1,
                    choices=[("N","Do nothing"),("G","Generate FQDNs"),("D","Partial reverse zone delegation")],default="N")),
            ('fqdn_template', models.CharField(_("FQDN Template"),max_length=255,null=True,blank=True)),
            ('reverse_nses', models.CharField(_("Reverse NSes"),max_length=255,null=True,blank=True)),
            ("tags", AutoCompleteTagsField("Tags",null=True,blank=True)),
            ("tt", models.IntegerField("TT",blank=True,null=True)),
            ("allocated_till", models.DateField("Allocated till",null=True,blank=True)),
        ))
        db.create_index('ip_addressrange', ['vrf_id','afi','from_address','to_address'], unique=True, db_tablespace='')
        
        # PrefixBookmark
        db.create_table('ip_prefixbookmark',(
            ('id',     models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ("user",   models.ForeignKey(User,verbose_name="User")),
            ("prefix", models.ForeignKey(Prefix,verbose_name="Prefix"))
        ))
        db.create_index('ip_prefixbookmark', ['user_id','prefix_id'], unique=True, db_tablespace='')
        
        db.send_create_signal('ip', ["Prefix","Address","PrefixBookmark"])

    def backwards(self):
        pass
