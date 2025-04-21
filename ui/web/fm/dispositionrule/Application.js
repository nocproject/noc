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
    "NOC.core.JSONPreviewII",
    "NOC.core.TemplatePreview",
    "NOC.core.ListFormField",
    "NOC.core.StringListField",
    "NOC.core.tagfield.Tagfield",
    "NOC.core.label.LabelField",
    "NOC.core.combotree.ComboTree",
    "NOC.fm.eventclass.LookupField",
    "NOC.fm.alarmclass.LookupField",
    "NOC.fm.dispositionrule.LookupField",
    "NOC.main.handler.LookupField",
    "NOC.main.remotesystem.LookupField",
    "NOC.main.notificationgroup.LookupField",
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
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/fm/dispositionrule/{id}/json/",
      previewName: "Disposition Rule: {name}",
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
          xtype: "fieldset",
          layout: "hbox",
          defaults: {
            margin: 5,
          },
          title: __("Object Actions"),
          items: [
            {
              name: "run_discovery",
              xtype: "checkbox",
              boxLabel: __("Run Discovery"),
            },
            {
              name: "interaction_audit",
              xtype: "combobox",
              fieldLabel: __("Audit"),
              allowBlank: true,
              store: [
                ["99", __("Run Command")],
                ["1", __("Login")],
                ["2", __("LogOut")],
                ["3", __("Reboot")],
                ["4", __("Started")],
                ["5", __("Halted")],
                ["6", __("Config Changed")],
              ],
              value: null,
              uiStyle: "medium",
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
          name: "vars_conditions",
          xtype: "gridfield",
          fieldLabel: __("Vars Conditions"),
          columns: [
            {
              text: __("Field"),
              dataIndex: "field",
              editor: "textfield",
              width: 250,
            },
            {
              text: __("Op"),
              dataIndex: "op",
              width: 100,
              editor: {
                xtype: "combobox",
                store: [
                  ["regex", __("Regex")],
                  ["contains", __("Contains")],
                  ["eq", __("Equal")],
                  ["ne", __("Not Equal")],
                  ["gte", __("Greater Equal")],
                  ["lte", __("Less Equal")],
                ],
              },
              renderer: NOC.render.Choices({
                "regex": __("Regex"),
                "contains": __("Contains"),
                "eq": __("Equal"),
                "ne": __("Not Equal"),
                "gte": __("Greater Equal"),
                "lte": __("Less Equal"),
              }),
            },
            {
              text: __("Value"),
              dataIndex: "value",
              editor: "textfield",
              flex: 1,
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
              uiStyle: "medium",
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
