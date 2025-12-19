//---------------------------------------------------------------------
// sa.actioncommands application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.actioncommands.Application");

Ext.define("NOC.sa.actioncommands.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.sa.actioncommands.Model",
    "NOC.sa.action.LookupField",
    "NOC.sa.profile.LookupField",
    "NOC.core.ListFormField",
    "Ext.ux.form.GridField",
    "Ext.ux.form.JSONField",
    "Ext.ux.form.GridField",

  ],
  model: "NOC.sa.actioncommands.Model",
  search: true,
  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/sa/actioncommands/{0}/json/",
      previewName: "Action Commands: {0}",
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 300,
        },
        {
          text: __("Builtin"),
          dataIndex: "is_builtin",
          width: 50,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Profile"),
          dataIndex: "profile",
          width: 100,
          renderer: NOC.render.Lookup("profile"),
        },
        {
          text: __("Preference"),
          dataIndex: "preference",
          width: 100,
          align: "right",
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "large",
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
        },
        {
          name: "action",
          xtype: "sa.action.LookupField",
          fieldLabel: __("Action"),
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          uiStyle: "extra",
        },
        {
          name: "profile",
          xtype: "sa.profile.LookupField",
          fieldLabel: __("Profile"),
          uiStyle: "medium",
          allowBlank: false,
        },
        {
          name: "config_mode",
          xtype: "checkbox",
          boxLabel: __("Config. Mode"),
        },
        {
          name: "exit_scope_commands",
          xtype: "textfield",
          fieldLabel: __("Exit Scope Commands"),
          uiStyle: "medium",
        },
        {
          name: "disable_when_change",
          xtype: "combobox",
          fieldLabel: __("Disable When Change"),
          store: [
            ["N", __("Nothing")],
            ["O", __("Out-of-Scope")],
            ["I", __("Inner-of-Scope")],
          ],
          value: "new",
          uiStyle: "medium",
        },
        {
          name: "preference",
          xtype: "numberfield",
          fieldLabel: __("Preference"),
          allowBlank: true,
        },
        {
          name: "timeout",
          xtype: "numberfield",
          fieldLabel: __("Timeout"),
          allowBlank: true,
        },
        {
          name: "match",
          xtype: "gridfield",
          fieldLabel: __("Match"),
          columns: [
            {
              text: __("Platform (Regex)"),
              dataIndex: "platform_re",
              editor: "textfield",
            },
            {
              text: __("Version (Regex)"),
              dataIndex: "version_re",
              editor: "textfield",
            },
          ],
        },
        {
          name: "scopes",
          xtype: "gridfield",
          fieldLabel: __("Scopes"),
          columns: [
            {
              text: __("Scope"),
              dataIndex: "scope",
              sortable: false,
              editor: "textfield",
              width: 100,
            },
            {
              text: __("Enter Scope"),
              dataIndex: "enter_scope",
              sortable: false,
              editor: "checkbox",
              width: 70,
            },
            {
              text: __("Command"),
              dataIndex: "command",
              sortable: false,
              editor: "textfield",
              width: 200,
            },
            {
              text: __("Exit Command"),
              dataIndex: "exit_command",
              sortable: false,
              editor: "textfield",
              width: 100,
            },
          ],
        },
        {
          name: "commands",
          xtype: "textarea",
          fieldLabel: __("Commands"),
          allowBlank: false,
          grow: true,
          growMin: 100, // Minimum height when growing
          growMax: 200, // Maximum height when growing
        },
        {
          name: "test_cases",
          xtype: "listform",
          rows: 3,
          fieldLabel: __("Test cases"),
          labelAlign: "top",
          items: [
            {
              xtype: "textarea",
              name: "output",
              width: 900,
              fieldLabel: __("Output"),
            },
            {
              xtype: "jsonfield",
              name: "context",
              fieldLabel: __("Context"),
              width: 500,
              editor: "jsonfield",
              renderer: NOC.render.JSON,
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

  filters: [
    {
      title: __("By SA Profile"),
      name: "profile",
      ftype: "lookup",
      lookup: "sa.profile",
    },
    {
      title: __("By Action"),
      name: "action",
      ftype: "lookup",
      lookup: "sa.action",
    },
  ],

  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
