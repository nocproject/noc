from south.db import db


class Migration:
    def forwards(self):
        return
        db.execute("CREATE INDEX x_managedobject_addressprefix ON sa_managedobject (CAST(address AS inet))")

    def backwards(self):
        db.drop_index("x_managedobject_addressprefix")
