//---------------------------------------------------------------------
// main.pool application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pool.Application");

Ext.define("NOC.main.pool.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.pool.Model",
  ],
  model: "NOC.main.pool.Model",
  search: true,
  helpId: "reference-pool",

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 100,
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
          fieldLabel: __("Name"),
          regex: /^[0-9a-zA-Z]{1,16}$/,
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
      ],
    });
    me.callParent();
  },
});
