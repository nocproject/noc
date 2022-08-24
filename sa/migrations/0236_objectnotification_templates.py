# ---------------------------------------------------------------------
# Initialize ObjectNotification Template
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

CONFIG_CHANGED = (
    "sa.mnaged_object.config_change",
    "managed_object_config_change",
    """Configuration changed notification

Context variables are
 * managed_object -- managed object instance
 * is_new -- True, if new config, False - otherwise
 * config -- Full config
 * diff -- unified diff, if is_new is false""",
    "{% if is_new %}New config for {{ managed_object.name }}{% else %}{{ managed_object.name }} config has been changed{% endif %}",
    """{% if is_new %}
{{config|safe}}
{% else %}
{{diff|safe}}
{% endif %}
""",
)
OBJECT_NEW = (
    "sa.mnaged_object.new",
    "managed_object_new",
    """Notify about new managed object

Context variables are:
   * managed_object - managed object instance""",
    "New managed object: {{ managed_object.name }}",
    """New managed object just has been created.
Name: {{ managed_object.name }}
Address: {{ managed_object.address }}
Profile: {{ managed_object.profile.name }}
""",
)
OBJECT_DELETE = (
    "sa.mnaged_object.delete",
    "managed_object_delete",
    """Notify about deleted managed object

Context variables are:
   * managed_object - managed object instance""",
    "New managed object: {{ managed_object.name }}",
    """Managed object just has been deleted.
Name: {{ managed_object.name }}
Address: {{ managed_object.address }}
Profile: {{ managed_object.profile.name }}
""",
)
CONFIG_POLICY_VIOLATION = (
    "sa.mnaged_object.config_policy_violation",
    "managed_object_config_policy_violation",
    """Configuration policy violation detected

Context variables are
 * managed_object -- managed object instance
 * warnings -- list of warnings""",
    "Configration policy violation at {{managed_object.name}}",
    """{% for w in warnings %}
{{forloop.counter}}. {{w}}
{% endfor %}
""",
)
VERSION_CHANGED = (
    "sa.mnaged_object.version_changed",
    "managed_object_version_changed",
    """ManagedObject Version changed notification

Context variables are
 * managed_object -- managed object instance
 * is_new -- True, if new version, False - otherwise
 * new -- New version
 * old -- Old version""",
    "{% if is_new %}New version for {{ managed_object.name }} ({{ managed_object.address }}) {% else %}{{ managed_object.name }} ({{ managed_object.address }}) version has been changed: {{old}} -> {{new}}{% endif %}",
    "",
)


class Migration(BaseMigration):
    depends_on = [("main", "0037_template")]

    def migrate(self):
        for name, sys_name, description, subject, body in [
            CONFIG_CHANGED,
            OBJECT_NEW,
            OBJECT_DELETE,
            CONFIG_POLICY_VIOLATION,
            VERSION_CHANGED,
        ]:
            self.db.execute(
                "INSERT INTO main_template(name, description, subject, body) VALUES(%s, %s, %s, %s)",
                [name, description, subject, body],
            )
            self.db.execute(
                """
                INSERT INTO main_systemtemplate(name, description, template_id)
                SELECT %s, %s, id
                FROM main_template
                WHERE name=%s
            """,
                [
                    sys_name,
                    "Interface status change notification",
                    name,
                ],
            )
