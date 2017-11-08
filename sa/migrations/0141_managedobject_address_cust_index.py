from south.db import db


class Migration:
    def forwards(self):
        func = """create or replace function cast_test_to_inet(varchar) returns inet as $$
        declare
             i inet;
        begin
             i := $1::inet;
             return i;
             EXCEPTION WHEN invalid_text_representation then
                    return '0.0.0.0'::inet;
        end;
        $$ language plpgsql immutable strict"""

        # Check index exists
        i = db.execute("""SELECT * FROM pg_indexes 
                          WHERE tablename='sa_managedobject' AND indexname='x_managedobject_addressprefix'""")
        if i:
            db.execute("DROP INDEX %s" % "x_managedobject_addressprefix")

        db.execute(func)
        db.execute("CREATE INDEX x_managedobject_addressprefix ON sa_managedobject (cast_test_to_inet(address))")

    def backwards(self):
        db.execute("DROP INDEX %s" % "x_managedobject_addressprefix")
        db.execute("DROP FUNCTION cast_test_to_inet")
