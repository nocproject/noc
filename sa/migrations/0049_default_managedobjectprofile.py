from south.db import db


class Migration:
    def forwards(self):
        db.execute("""
        INSERT INTO sa_managedobjectprofile(name)
        VALUES('default')
        """)

    def backwards(self):
        pass
