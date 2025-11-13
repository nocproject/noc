//---------------------------------------------------------------------
// fm.dispositionrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.dispositionrule.Application");

Ext.define("NOC.fm.dispositionrule.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreview",
    "NOC.core.TemplatePreview",
    "NOC.core.ListFormField",
    "NOC.core.StringListField",
    "NOC.core.tagfield.Tagfield",
    "NOC.core.StringListField",
    "NOC.core.label.LabelField",
    "NOC.core.combotree.ComboTree",
    "NOC.fm.eventclass.LookupField",
    "NOC.fm.alarmclass.LookupField",
    "NOC.fm.dispositionrule.LookupField",
    "NOC.main.handler.LookupField",
    "NOC.main.remotesystem.LookupField",
    "NOC.main.notificationgroup.LookupField",
    "NOC.sa.action.LookupField",
    "Ext.ux.form.JSONField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.fm.dispositionrule.Model",
  search: true,
  treeFilter: "category",
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      width: 500,
    },
    {
      text: __("Builtin"),
      dataIndex: "is_builtin",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Alarm Disposition"),
      dataIndex: "alarm_disposition",
      flex: 1,
      renderer: NOC.render.Lookup("alarm_disposition"),
    },
    {
      text: __("Pref"),
      dataIndex: "preference",
      width: 50,
    },
    {
      text: __("Action"),
      dataIndex: "default_action",
      width: 50,
    },
  ],
  filters: [
    {
      title: __("By Event Class"),
      name: "event_class",
      ftype: "lookup",
      lookup: "fm.eventclass",
    },
    {
      title: __("By Alarm Class"),
      name: "alarm_disposition",
      ftype: "lookup",
      lookup: "fm.alarmclass",
    },
  ],

  initComponent: function(){
    var me = this;
    me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
      app: me,
      restUrl: "/fm/dispositionrule/{0}/json/",
      previewName: "Disposition Rule: {0}",
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    //
    Ext.apply(me, {
      fields: [
        {
          xtype: "textfield",
          name: "name",
          fieldLabel: __("Name"),
          allowBlank: false,
        },
        {
          xtype: "displayfield",
          name: "uuid",
          fieldLabel: __("UUID"),
        },
        {
          xtype: "textarea",
          name: "description",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "is_active",
          xtype: "checkbox",
          boxLabel: __("Active"),
        },
        {
          xtype: "numberfield",
          name: "preference",
          fieldLabel: __("Preference"),
          allowBlank: false,
          uiStyle: "small",
          defaultValue: 1000,
          minValue: 0,
          maxValue: 10000,
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          defaults: {
            labelAlign: "top",
            margin: 5,
          },
          title: __("Combo Condition"),
          items: [
            {
              name: "combo_condition",
              xtype: "combobox",
              fieldLabel: __("Combo Condition"),
              store: [
                ["none", __("None")],
                ["frequency", __("Frequency")],
                ["sequence", __("Sequence")],
                ["all", __("All")],
                ["any", __("Any")],
              ],
              value: "none",
              uiStyle: "medium",
            },
            {
              name: "combo_window",
              xtype: "numberfield",
              fieldLabel: __("Combo Window (sec)"),
              allowBlank: true,
              uiStyle: "medium",
              defaultValue: 0,
              minValue: 0,
            },
            {
              name: "combo_count",
              xtype: "numberfield",
              fieldLabel: __("Combo count"),
              allowBlank: true,
              uiStyle: "medium",
              defaultValue: 0,
              minValue: 0,
            },
          ],
        },
        {
          xtype: "fieldset",
          title: __("Replace Rule"),
          layout: "hbox",
          defaults: {
            labelAlign: "left",
            margin: 5,
          },
          items: [
            {
              name: "replace_rule",
              xtype: "fm.dispositionrule.LookupField",
              fieldLabel: __("Dispose Rule"),
              uiStyle: "medium",
              allowBlank: true,
            },
            {
              name: "replace_rule_policy",
              xtype: "combobox",
              fieldLabel: __("Replace Policy"),
              store: [
                ["D", __("Disable")],
                ["w", __("Whole")],
                ["c", __("Extend Condition")],
                ["a", __("Action")],
              ],
              value: "none",
              uiStyle: "medium",
            },
          ],
        },
        {
          name: "handlers",
          xtype: "gridfield",
          fieldLabel: __("Handlers"),
          columns: [
            {
              text: __("Handler"),
              dataIndex: "handler",
              width: 400,
              editor: {
                xtype: "main.handler.LookupField",
              },
              renderer: NOC.render.Lookup("handler"),
            },
          ],
        },
        {
          name: "target_actions",
          xtype: "gridfield",
          fieldLabel: __("Run Actions"),
          columns: [
            {
              text: __("Action"),
              dataIndex: "action",
              width: 150,
              allowBlank: false,
              editor: {
                xtype: "combobox",
                store: [
                  ["action_command", __("Action Command")],
                  ["audit_command", __("Audit")],
                  ["run_discovery", __("Run Discovery")],
                  ["fire_wf_event", __("Fire Event")],
                ],
              },
              renderer: NOC.render.Choices({
                "action_command": __("Action Command"),
                "audit_command": __("Audit"),
                "run_discovery": __("Run Discovery"),
                "fire_wf_event": __("Fire Event"),
              }),
            },
            {
              text: __("Audit"),
              dataIndex: "interaction_audit",
              width: 100,
              editor: {
                xtype: "combobox",
                store: [
                  [0, __("TTL")],
                  [1, __("Login")],
                  [2, __("LogOut")],
                  [3, __("Reboot")],
                  [4, __("Started")],
                  [5, __("Halted")],
                  [6, __("Config Changed")],
                ],
              },
              renderer: NOC.render.Choices({
                0: __("TTL"),
                1: __("Login"),
                2: __("LogOut"),
                3: __("Reboot"),
                4: __("Started"),
                5: __("Halted"),
                6: __("Config Changed"),
              }),
            },
            {
              text: __("Action Command"),
              dataIndex: "action_command",
              width: 300,
              editor: {
                xtype: "sa.action.LookupField",
              },
              renderer: NOC.render.Lookup("action_command"),
            },
            {
              editor: "stringlistfield",
              dataIndex: "context",
              width: 400,
              text: __("Context"),
            },
          ],
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          defaults: {
            labelAlign: "top",
            margin: 5,
          },
          title: __("Notification"),
          items: [
            {
              name: "notification_group",
              xtype: "main.notificationgroup.LookupField",
              fieldLabel: __("New Event Notification"),
              labelWidth: 200,
              allowBlank: true,
            },
          ],
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          defaults: {
            labelAlign: "top",
            margin: 5,
          },
          title: __("Disposition"),
          items: [
            {
              name: "alarm_disposition",
              xtype: "fm.alarmclass.LookupField",
              fieldLabel: __("Dispose Alarm"),
              uiStyle: "medium",
              allowBlank: true,
            },
            {
              name: "default_action",
              xtype: "combobox",
              fieldLabel: __("Default Action"),
              store: [
                ["R", __("Raise Alarm")],
                ["I", __("Ignore Disposition")],
                ["C", __("Clear Alarm")],
                ["D", __("Drop Event")],
                ["F", __("Drop Event (with MX)")],
              ],
              uiStyle: "medium",
            },
          ],
        },
        {
          name: "stop_processing",
          xtype: "checkbox",
          boxLabel: __("Stop Processing Rules"),
        },
        {
          name: "vars_conditions_op",
          xtype: "combobox",
          fieldLabel: __("Condition Op Vars"),
          store: [
            ["AND", __("AND")],
            ["OR", __("OR")],
          ],
          uiStyle: "medium",
        },
        {
          name: "vars_op",
          xtype: "gridfield",
          fieldLabel: __("Vars Operations"),
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              editor: "textfield",
              width: 150,
            },
            {
              text: __("Required"),
              dataIndex: "required",
              width: 50,
              editor: "checkboxfield",
              renderer: NOC.render.Bool,
            },
            {
              text: __("Cond."),
              dataIndex: "condition",
              width: 100,
              editor: {
                xtype: "combobox",
                store: [
                  ["regex", __("Regex")],
                  ["contains", __("Contains")],
                  ["exists", __("Exists")],
                  ["eq", __("Equal")],
                  ["ne", __("Not Equal")],
                  ["gte", __("Greater Equal")],
                  ["gt", __("Greater")],
                  ["lte", __("Less Equal")],
                  ["lt", __("Less")],
                ],
              },
              renderer: NOC.render.Choices({
                "regex": __("Regex"),
                "contains": __("Contains"),
                "exists": __("Exists"),
                "eq": __("Equal"),
                "ne": __("Not Equal"),
                "gte": __("Greater Equal"),
                "gt": __("Greater"),
                "lte": __("Less Equal"),
                "lt": __("Less"),
              }),
            },
            {
              text: __("Value"),
              dataIndex: "value",
              editor: "textfield",
              width: 100,
            },
            {
              text: __("Choices (for multi)"),
              dataIndex: "choices",
              width: 100,
              editor: "stringlistfield",
            },
            {
              text: __("Value Type"),
              dataIndex: "value_type",
              width: 100,
              editor: {
                xtype: "combobox",
                store: [
                  "str",
                  "int", "float",
                  "ipv4_address", "ipv6_address", "ip_address",
                  "ipv4_prefix", "ipv6_prefix", "ip_prefix",
                  "mac", "interface_name", "oid", "http_url",
                ],
              },
            },
            {
              text: __("Alias"),
              dataIndex: "alias",
              editor: "textfield",
              width: 100,
            },
            {
              text: __("Affected"),
              dataIndex: "affected_model",
              width: 100,
              editor: {
                xtype: "combobox",
                store: [
                  ["sa.ManagedObject", __("Managed Object")],
                  ["sa.Service", __("Service")],
                  ["inv.Interface", __("Interface")],
                  ["peer.Peer", __("IP Peer")],
                ],
              },
              renderer: NOC.render.Choices({
                "sa.ManagedObject": __("Managed Object"),
                "sa.Service": __("Service"),
                "inv.Interface": __("Interface"),
                "peer.Peer": __("IP Peer"),
              }),
            },
            {
              text: __("Oper Status"),
              dataIndex: "update_oper_status",
              width: 100,
              editor: {
                xtype: "combobox",
                store: [
                  ["N", __("Disable")],
                  ["U", __("Up")],
                  ["D", __("Down")],
                  ["V", __("By Var")],
                ],
              },
              renderer: NOC.render.Choices({
                "N": __("Disable"),
                "U": __("Up"),
                "D": __("Down"),
                "V": __("By Var"),
              }),
            },
          ],
        },
        {
          name: "conditions",
          xtype: "listform",
          fieldLabel: __("Match Rules"),
          rows: 5,
          items: [
            {
              name: "event_class_re",
              xtype: "textfield",
              fieldLabel: __("Event Class RE"),
              uiStyle: "large",
              allowBlank: true,
            },
            {
              name: "labels",
              xtype: "labelfield",
              fieldLabel: __("Match Labels"),
              allowBlank: true,
              isTree: true,
              filterProtected: false,
              pickerPosition: "down",
              uiStyle: "extra",
              query: {
                "allow_matched": true,
              },
            },
            {
              xtype: "core.tagfield",
              url: "/inv/resourcegroup/lookup/",
              fieldLabel: __("Object Groups"),
              name: "groups",
              allowBlank: true,
              uiStyle: "extra",
            },
            {
              name: "remote_system",
              xtype: "main.remotesystem.LookupField",
              fieldLabel: __("Remote System"),
              allowBlank: true,
            },
            {
              name: "reference_rx",
              xtype: "textfield",
              fieldLabel: __("Group Reference Regex"),
              uiStyle: "large",
              allowBlank: true,
            },
            {
              name: "object_status",
              xtype: "combobox",
              fieldLabel: __("Object Avail"),
              store: [
                ["A", __("Any")],
                ["D", __("To DOWN")],
                ["U", __("To UP")],
              ],
              uiStyle: "medium",
            },
          ],
        },

      ],
      formToolbar: [
        {
          text: __("JSON"),
          glyph: NOC.glyph.file,
          tooltip: __("Show JSON"),
          hasAccess: NOC.hasPermission("read"),
          scope: me,
          handler: me.onJSON,
        },
      ],
    });
    me.callParent();
  },

  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
