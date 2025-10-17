//---------------------------------------------------------------------
// main.sync application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.sync.Application");

Ext.define("NOC.main.sync.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.sync.Model",
    "NOC.aaa.user.LookupField",
  ],
  model: "NOC.main.sync.Model",
  search: true,

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
          text: __("Active"),
          dataIndex: "is_active",
          renderer: NOC.render.Bool,
          width: 50,
        },
        {
          text: __("Instances"),
          dataIndex: "n_instances",
          width: 70,
          align: "right",
        },
        {
          text: __("Credentials"),
          dataIndex: "user",
          width: 100,
          renderer: NOC.render.Lookup("user"),
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          allowBlank: false,
          fieldLabel: __("Name"),
          regex: /^[a-z0-9.\-_]+$/i,
        },
        {
          name: "is_active",
          xtype: "checkboxfield",
          boxLabel: __("Active"),
        },
        {
          name: "user",
          xtype: "aaa.user.LookupField",
          fieldLabel: __("Credentials"),
        },
        {
          name: "n_instances",
          xtype: "numberfield",
          fieldLabel: __("Instances"),
          minValue: 1,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
      ],
      filters: [
        {
          title: __("Active"),
          name: "is_active",
          ftype: "boolean",
        },
      ],
    });
    me.callParent();
  },
});
