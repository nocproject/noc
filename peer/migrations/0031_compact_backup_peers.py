# -*- coding: utf-8 -*-

<<<<<<< HEAD
# Third-party modules
from south.db import db


class Migration(object):

    def forwards(self):
        backup = {}  # backup_id->(primary_id,local_backup_ip,remote_backup_ip)
        peers = db.execute(
            "SELECT id,peering_point_id,peer_group_id,local_asn_id,remote_asn,local_pref,import_filter,export_filter FROM peer_peer")
        for peer_id, peering_point_id, peer_group_id, local_asn_id, remote_asn, local_pref, import_filter, export_filter in peers:
            if peer_id in backup:
                continue
            r = db.execute("""SELECT id,local_ip,remote_ip
=======
from south.db import db
from django.db import models
from noc.peer.models import *

class Migration:
    
    def forwards(self):
        backup={} # backup_id->(primary_id,local_backup_ip,remote_backup_ip)
        peers=db.execute("SELECT id,peering_point_id,peer_group_id,local_asn_id,remote_asn,local_pref,import_filter,export_filter FROM peer_peer")
        for peer_id,peering_point_id,peer_group_id,local_asn_id,remote_asn,local_pref,import_filter,export_filter in peers:
            if peer_id in backup:
                continue
            r=db.execute("""SELECT id,local_ip,remote_ip
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                            FROM peer_peer
                            WHERE id!=%s
                                AND peering_point_id=%s
                                AND peer_group_id=%s
                                AND local_asn_id=%s
                                AND remote_asn=%s
                                AND local_pref=%s
                                AND import_filter=%s
                                AND export_filter=%s ORDER BY local_ip DESC""",
<<<<<<< HEAD
                           [peer_id, peering_point_id, peer_group_id, local_asn_id, remote_asn,
                            local_pref,
                            import_filter, export_filter])
            if r:
                backup_id, local_backup_ip, remote_backup_ip = r[0]
                backup[backup_id] = (peer_id, local_backup_ip, remote_backup_ip)
        # Compact backup sessions
        for backup_id, args in backup.items():
            peer_id, local_backup_ip, remote_backup_ip = args
            db.execute("UPDATE peer_peer SET local_backup_ip=%s,remote_backup_ip=%s WHERE id=%s",
                       [local_backup_ip, remote_backup_ip, peer_id])
            db.execute("DELETE FROM peer_peer WHERE id=%s", [backup_id])

=======
                                [peer_id,peering_point_id,peer_group_id,local_asn_id,remote_asn,local_pref,
                                    import_filter,export_filter])
            if r:
                backup_id,local_backup_ip,remote_backup_ip=r[0]
                backup[backup_id]=(peer_id,local_backup_ip,remote_backup_ip)
        # Compact backup sessions
        for backup_id,args in backup.items():
            peer_id,local_backup_ip,remote_backup_ip=args
            db.execute("UPDATE peer_peer SET local_backup_ip=%s,remote_backup_ip=%s WHERE id=%s",[local_backup_ip,remote_backup_ip,peer_id])
            db.execute("DELETE FROM peer_peer WHERE id=%s",[backup_id])
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        pass
