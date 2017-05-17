from south.db import db
from django.db import models

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


class Migration:
    def forwards(self):
        db.drop_index("x_managedobject_addressprefix")
        db.execute(func)
        db.execute("CREATE INDEX x_managedobject_addressprefix ON sa_managedobject (cast_test_to_inet(address))")

    def backwards(self):
        db.drop_index("x_managedobject_addressprefix")
        db.execute("DROP FUNCTION cast_test_to_inet")
