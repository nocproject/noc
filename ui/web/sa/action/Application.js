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
    "NOC.sa.action.Model",
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
          xtype: "textfield",
          fieldLabel: __("Handler"),
          allowBlank: true,
          uiStyle: "large",
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
                  ["str", "str"],
                  ["float", "float"],
                  ["int", "int"],
                  ["interface", "interface"],
                  ["ip", "ip"],
                  ["vrf", "vrf"],
                ],
              },
            },
            {
              text: __("Default"),
              dataIndex: "default",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Description"),
              dataIndex: "description",
              flex: 1,
              editor: "textfield",
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
