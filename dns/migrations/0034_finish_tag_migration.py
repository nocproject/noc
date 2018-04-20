# encoding: utf-8
from south.db import db

class Migration:
    TAG_MODELS = ["dns_dnszone", "dns_dnszonerecord"]

    def forwards(self):
        # Drop old tags
        for m in self.TAG_MODELS:
            db.drop_column(m, "tags")
        # Rename new tags
        for m in self.TAG_MODELS:
            db.rename_column(m, "tmp_tags", "tags")
        # Create indexes
        for m in self.TAG_MODELS:
            db.execute("CREATE INDEX x_%s_tags ON \"%s\" USING GIN(\"tags\")" % (m, m))

    def backwards(self):
<<<<<<< HEAD
        pass
=======
        pass
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
