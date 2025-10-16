//---------------------------------------------------------------------
// main.refbookadmin application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.refbookadmin.Application");

Ext.define("NOC.main.refbookadmin.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.refbookadmin.Model",
    "NOC.main.language.LookupField",
    "NOC.main.refbookadmin.FieldsModel",
    "NOC.main.refbookadmin.LookupField",
  ],
  model: "NOC.main.refbookadmin.Model",
  recordReload: true,
  maskElement: "el",
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Language"),
          dataIndex: "language",
          renderer: NOC.render.Lookup("language"),
          width: 200,
        },
        {
          text: __("Is Builtin"),
          dataIndex: "is_builtin",
          width: 100,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Is Enabled"),
          dataIndex: "is_enabled",
          width: 100,
          renderer: NOC.render.Bool,
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
          name: "language",
          xtype: "main.language.LookupField",
          fieldLabel: __("Language"),
          allowBlank: false,
          query: {
            "is_active": true,
          },
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
          uiStyle: "large",
        },
        {
          name: "is_builtin",
          xtype: "checkboxfield",
          boxLabel: __("Is Builtin"),
          boxLabelAlign: "before",
          allowBlank: false,
          uiStyle: "small",
        },
        {
          name: "is_enabled",
          xtype: "checkboxfield",
          boxLabel: __("Is Enabled"),
          boxLabelAlign: "before",
          allowBlank: false,
          uiStyle: "small",
        },
        {
          name: "refresh_interval",
          xtype: "numberfield",
          fieldLabel: __("Refresh Interval (days)"),
          allowBlank: false,
          min: 0,
          uiStyle: "small",
        },
        {
          name: "last_updated",
          xtype: "datefield",
          startDay: 1,
          format: "d.m.Y G:i",
          fieldLabel: __("Last Updated"),
          allowBlank: true,
          disabled: true,
          uiStyle: "medium",
        },
        {
          name: "next_update",
          xtype: "datefield",
          startDay: 1,
          format: "d.m.Y G:i",
          fieldLabel: __("Next Updated"),
          allowBlank: true,
          disabled: true,
          uiStyle: "medium",
        },
      ],
    });
    me.callParent();
  },
  filters: [
    {
      title: __("By Builtin"),
      name: "is_builtin",
      ftype: "boolean",
    },
    {
      title: __("By Enabled"),
      name: "is_enabled",
      ftype: "boolean",
    },
  ],
  inlines: [
    {
      title: __("Ref Book Fields"),
      collapsed: true,
      model: "NOC.main.refbookadmin.FieldsModel",
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          editor: "textfield",
        },
        {
          text: __("Order"),
          dataIndex: "order",
          editor: "numberfield",
        },
        {
          text: __("Req."),
          dataIndex: "is_required",
          editor: "checkboxfield",
          width: 50,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          editor: "textfield",
        },
        {
          text: __("Search Method"),
          dataIndex: "search_method",
          editor: "main.refbookadmin.LookupField",
          width: 150,
        },
      ],
    },
  ],
});