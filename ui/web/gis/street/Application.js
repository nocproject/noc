//---------------------------------------------------------------------
// gis.street application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.street.Application");

Ext.define("NOC.gis.street.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.gis.street.Model",
    "NOC.gis.division.LookupField",
  ],
  model: "NOC.gis.street.Model",
  search: true,
  treeFilter: "parent",

  initComponent: function(){
    var me = this;

    Ext.apply(me, {
      columns: [
        {
          text: __("Short"),
          dataIndex: "short_name",
          width: 50,
        },
        {
          text: __("Name"),
          dataIndex: "name",
          width: 300,
        },
        {
          text: __("Active"),
          dataIndex: "is_active",
          renderer: NOC.render.Bool,
          width: 25,
        },
        {
          text: __("Parent"),
          dataIndex: "full_parent",
          flex: 1,
          sort: false,
        },
        {
          text: __("Remote System"),
          dataIndex: "remote_system",
          flex: 1,
          sort: false,
        },
        {
          text: __("Remote Id"),
          dataIndex: "remote_id",
          flex: 1,
          sort: false,
        },
      ],
      fields: [
        {
          name: "full_path",
          xtype: "displayfield",
          fieldLabel: __("Full Path"),
        },
        {
          name: "parent",
          xtype: "gis.division.LookupField",
          fieldLabel: __("Parent"),
        },
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
        },
        {
          name: "short_name",
          xtype: "textfield",
          fieldLabel: __("Short Name"),
          allowBlank: true,
        },
        {
          name: "is_active",
          xtype: "checkboxfield",
          boxLabel: __("Active"),
        },
        {
          xtype: "dictfield",
          name: "data",
          fieldLabel: __("Data"),
          allowBlank: true,
        },
      ],
    });
    me.callParent();
  },
  filters: [
    {
      title: __("By Parent"),
      name: "parent",
      ftype: "lookup",
      lookup: "gis.division",
    },
  ],
});
