//---------------------------------------------------------------------
// sa.action application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.action.Application");

Ext.define("NOC.sa.action.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreviewII",
    "NOC.main.handler.LookupField",
    "NOC.sa.action.Model",
    "NOC.core.StringListField",
    "NOC.sa.action.LookupField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.sa.action.Model",
  search: true,

  initComponent: function(){
    var me = this;

    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/sa/action/{0}/json/",
      previewName: "Action: {0}",
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Label"),
          dataIndex: "Label",
          width: 200,
        },
        {
          text: __("Builtin"),
          dataIndex: "is_builtin",
          width: 50,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
        {
          text: __("Lvl"),
          dataIndex: "access_level",
          width: 50,
        },
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "medium",
          regex: /^[a-zA-Z_][a-zA-Z_\-0-9]*$/,
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
        },
        {
          name: "label",
          xtype: "textfield",
          fieldLabel: __("Label"),
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
          name: "access_level",
          xtype: "numberfield",
          fieldLabel: __("Access Level"),
          value: 15,
          minValue: 0,
          maxValue: 15,
          uiStyle: "small",
        },
        {
          name: "handler",
          xtype: "main.handler.LookupField",
          fieldLabel: __("Handler"),
          query: {
            allow_action: true
          },
          allowBlank: true,
          uiStyle: "medium",
        },
        {
          name: "params",
          xtype: "gridfield",
          fieldLabel: __("Params"),
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              width: 150,
              editor: {
                xtype: "textfield",
                regex: /^[a-zA-Z_][a-zA-Z_\-0-9]*$/,
              },
            },
            {
              text: __("Required"),
              dataIndex: "is_required",
              width: 50,
              editor: "checkbox",
              renderer: NOC.render.Bool,
            },
            {
              text: __("Type"),
              dataIndex: "type",
              width: 100,
              editor: {
                xtype: "combobox",
                store: [
                  ["bool", "Boolean"],
                  ["str", "String"],
                  ["int", "Integer"],
                  ["float", "Float"],
                  ["mac", "MAC Address"],
                  ["interface_name", "Interface"],
                  ["vlan", "Vlan Num"],
                  ["ip_address", "IP Address"],
                  ["ip_vrf", "IP VRF"]
                ],
              },
            },
            {
              text: __("Multi"),
              dataIndex: "multi",
              width: 50,
              editor: "checkbox",
              renderer: NOC.render.Bool,
            },
            {
              text: __("Default"),
              dataIndex: "default",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Scope"),
              dataIndex: "scope",
              flex: 100,
              editor: "textfield",
            },
            {
              text: __("Scope Command"),
              dataIndex: "scope_command",
              flex: 200,
              editor: "textfield",
            },
            {
              text: __("Scope Exit"),
              dataIndex: "scope_exit",
              flex: 100,
              editor: "textfield",
            },
            {
              text: __("Description"),
              dataIndex: "description",
              flex: 100,
              editor: "textfield",
            },
          ],
        },
        {
          name: "action_set",
          xtype: "gridfield",
          fieldLabel: __("Action Set"),
          columns: [
            {
              text: __("Action"),
              dataIndex: "action",
              width: 200,
              renderer: NOC.render.Lookup("action"),
              editor: {
                xtype: "core.combo",
                restUrl: "/sa/action/lookup/",
              },
            },
            {
              text: __("Execute"),
              dataIndex: "execute",
              width: 150,
              editor: {
                xtype: "combobox",
                store: [
                  ["S", __("Set")],
                  ["D", __("Disable Scope")],
                  ["E", __("Enable Scope")],
                  ["R", __("Rollback")],
                ],
              },
              renderer: NOC.render.Choices({
                "S": __("Set"),
                "D": __("Disable Scope"),
                "E": __("Enable Scope"),
                "R": __("Rollback"),
              }),
            },
            {
              text: __("Cancel"),
              dataIndex: "cancel",
              editor: "checkbox",
              renderer: NOC.render.Bool,
            },
            {
              editor: "stringlistfield",
              dataIndex: "domain_scopes",
              width: 200,
              text: __("Domain Scopes"),
            },
            {
              editor: "stringlistfield",
              dataIndex: "params_ctx",
              width: 400,
              text: __("Params Map"),
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
