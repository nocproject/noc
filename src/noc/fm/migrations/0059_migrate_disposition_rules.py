# ----------------------------------------------------------------------
# Empty migration: disposition rules stay on EventClass.
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        pass
