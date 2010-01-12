# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.peer.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Peer.remote_backup_ip'
        db.add_column('peer_peer', 'remote_backup_ip', orm['peer.Peer:remote_backup_ip'])
        
        # Adding field 'Peer.local_backup_ip'
        db.add_column('peer_peer', 'local_backup_ip', orm['peer.Peer:local_backup_ip'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Peer.remote_backup_ip'
        db.delete_column('peer_peer', 'remote_backup_ip')
        
        # Deleting field 'Peer.local_backup_ip'
        db.delete_column('peer_peer', 'local_backup_ip')
        
    
    
    models = {
        'main.notificationgroup': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'peer.as': {
            'administrative_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['peer.Person']"}),
            'as_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'asn': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'footer_remarks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'header_remarks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['peer.Maintainer']"}),
            'organisation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.Organisation']"}),
            'rir': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.RIR']"}),
            'routes_maintainers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['peer.Maintainer']"}),
            'tech_contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['peer.Person']"})
        },
        'peer.asset': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'rpsl_footer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'rpsl_header': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'peer.community': {
            'community': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.CommunityType']"})
        },
        'peer.communitytype': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'peer.maintainer': {
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['peer.Person']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'extra': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintainer': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'rir': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.RIR']"})
        },
        'peer.organisation': {
            'address': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mnt_ref': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.Maintainer']"}),
            'org_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'org_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'organisation': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'peer.peer': {
            'communities': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'export_filter': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'export_filter_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_filter': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'import_filter_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'local_asn': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.AS']"}),
            'local_backup_ip': ('INETField', ['"Local Backup IP"'], {'null': 'True', 'blank': 'True'}),
            'local_ip': ('INETField', ['"Local IP"'], {}),
            'local_pref': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_prefixes': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'peer_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.PeerGroup']"}),
            'peering_point': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.PeeringPoint']"}),
            'remote_asn': ('django.db.models.fields.IntegerField', [], {}),
            'remote_backup_ip': ('INETField', ['"Remote Backup IP"'], {'null': 'True', 'blank': 'True'}),
            'remote_ip': ('INETField', ['"Remote IP"'], {}),
            'rpsl_remark': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'tt': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'peer.peergroup': {
            'communities': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_prefixes': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'peer.peeringpoint': {
            'communities': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'enable_prefix_list_provisioning': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_as': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.AS']"}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'prefix_list_notification_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.NotificationGroup']", 'null': 'True', 'blank': 'True'}),
            'profile_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'router_id': ('django.db.models.fields.IPAddressField', [], {'unique': 'True', 'max_length': '15'})
        },
        'peer.person': {
            'address': ('django.db.models.fields.TextField', [], {}),
            'email': ('django.db.models.fields.TextField', [], {}),
            'extra': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fax_no': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nic_hdl': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'person': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('django.db.models.fields.TextField', [], {}),
            'rir': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.RIR']"})
        },
        'peer.prefixlistcache': {
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('InetArrayField', ['"Data"'], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'peering_point': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.PeeringPoint']"}),
            'pushed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'strict': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'peer.rir': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'whois': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'peer.whoiscache': {
            'Meta': {'unique_together': "[('lookup', 'key')]"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'lookup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.WhoisLookup']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'peer.whoisdatabase': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'peer.whoislookup': {
            'Meta': {'unique_together': "[('whois_database', 'url', 'key', 'value')]"},
            'direction': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'whois_database': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['peer.WhoisDatabase']"})
        }
    }
    
    complete_apps = ['peer']
