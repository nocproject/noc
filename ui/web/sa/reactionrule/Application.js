//---------------------------------------------------------------------
// sa.reactionrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.reactionrule.Application");

Ext.define("NOC.sa.reactionrule.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
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
    "NOC.inv.capability.LookupField",
    "NOC.sa.action.LookupField",
    "NOC.sa.reactionrule.LookupField",
    "NOC.main.ref.modelid.LookupField",
    "Ext.ux.form.JSONField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.sa.reactionrule.Model",
  search: true,

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
  ],

  initComponent: function(){
    var me = this;
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/sa/reactionrule/{0}/json/",
      previewName: "Reaction Rule: {0}",
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
          name: "object_model",
          xtype: "combobox",
          fieldLabel: __("Object Class"),
          allowBlank: false,
          store: [
            ["sa.ManagedObject", __("Managed Object")],
            ["sa.Service", __("Service")],
            ["sla.SLAProbe", __("SLA Probe")],
            ["inv.Interface", __("Network Interface")],
            ["inv.Object", __("Inventory object")],
            ["vc.L2Domain", __("L2 Domain")],
            ["vc.VLAN", __("VLAN")],
          ],
          uiStyle: "medium",
        },
        {
          name: "operations",
          xtype: "tagfield",
          fieldLabel: __("Operations"),
          allowBlank: false,
          store: [
            ["create", __("Create")],
            ["update", __("Update")],
            ["delete", __("Delete")],
            ["topology", __("Topology")],
            ["config_changed", __("Config Changed")],
            ["version_changed", __("Version Changed")],
            ["version_set", __("Version Set")],
            ["any", __("Any")],
          ],
          uiStyle: "medium",
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
          name: "field_data",
          xtype: "gridfield",
          fieldLabel: __("Field Data"),
          columns: [
            {
              text: __("Field"),
              dataIndex: "field",
              editor: "textfield",
              width: 250,
            },
            {
              text: __("Capability"),
              dataIndex: "capability",
              renderer: NOC.render.Lookup("capability"),
              width: 250,
              editor: "inv.capability.LookupField",
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
              text: __("Set Context"),
              dataIndex: "set_context",
              editor: "textfield",
              width: 100,
            },
          ],
        },
        {
          name: "affected_rules",
          xtype: "gridfield",
          fieldLabel: __("Affected Rules"),
          columns: [
            {
              text: __("ModelID"),
              dataIndex: "model_id",
              renderer: NOC.render.Lookup("model_id"),
              editor: "main.ref.modelid.LookupField",
              width: 150,
            },
            {
              text: __("Rule"),
              dataIndex: "rule",
              renderer: NOC.render.Lookup("rule"),
              editor: "sa.reactionrule.LookupField",
              width: 150,
            },
            {
              text: __("Suppress Action"),
              dataIndex: "suppress_action",
              width: 70,
              editor: "checkboxfield",
              renderer: NOC.render.Bool,
            },
            {
              text: __("Extend Ctx"),
              dataIndex: "extend_ctx",
              width: 70,
              editor: "checkboxfield",
              renderer: NOC.render.Bool,
            },
          ],
        },
        {
          name: "actions",
          xtype: "gridfield",
          fieldLabel: __("Run Actions"),
          columns: [
            {
              text: __("Action"),
              dataIndex: "action",
              width: 100,
              allowBlank: false,
              editor: {
                xtype: "combobox",
                store: [
                  ["handler", __("Handler")],
                  ["action_command", __("Commands")],
                  ["run_discovery", __("Run Discovery")],
                  ["fire_wf_event", __("Fire Event")],
                ],
              },
              renderer: NOC.render.Choices({
                "handler": __("Handler"),
                "action_command": __("Commands"),
                "run_discovery": __("Run Discovery"),
                "fire_wf_event": __("Fire Event"),
              }),
            },
            {
              text: __("Run"),
              dataIndex: "run",
              width: 75,
              allowBlank: false,
              editor: {
                xtype: "combobox",
                store: [
                  ["A", __("Always")],
                  ["F", __("Prev Failed")],
                  ["S", __("Prev Success")],
                ],
              },
              renderer: NOC.render.Choices({
                "A": __("Always"),
                "F": __("Prev Failed"),
                "S": __("Prev Successy"),
              }),
            },
            {
              text: __("Commands"),
              dataIndex: "commands",
              width: 150,
              editor: {
                xtype: "sa.action.LookupField",
              },
              renderer: NOC.render.Lookup("commands"),
            },
            {
              text: __("Allow Fail"),
              dataIndex: "allow_fail",
              width: 50,
              editor: "checkboxfield",
              renderer: NOC.render.Bool,
            },
            {
              text: __("Cancel"),
              dataIndex: "cancel_command",
              width: 50,
              editor: "checkboxfield",
              renderer: NOC.render.Bool,
            },
            {
              text: __("Domain Ctx"),
              dataIndex: "expand_domain_ctx",
              width: 70,
              editor: "checkboxfield",
              renderer: NOC.render.Bool,
            },
            {
              text: __("Over Topology"),
              dataIndex: "over_topology",
              width: 70,
              editor: "checkboxfield",
              renderer: NOC.render.Bool,
            },
            {
              editor: "stringlistfield",
              dataIndex: "context",
              width: 400,
              text: __("Context"),
            },
            {
              text: __("Handler"),
              dataIndex: "handler",
              width: 150,
              editor: {
                xtype: "main.handler.LookupField",
                query: {
                  allow_reaction: true,
                },
              },
              renderer: NOC.render.Lookup("handler"),
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
          name: "conditions",
          xtype: "listform",
          fieldLabel: __("Match Rules"),
          rows: 5,
          items: [
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
              xtype: "core.tagfield",
              url: "/wf/state/lookup/",
              fieldLabel: __("WF States"),
              name: "wf_states",
              allowBlank: true,
              uiStyle: "extra",
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
