//---------------------------------------------------------------------
// main.datastreamconfig application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.datastreamconfig.Application");

Ext.define("NOC.main.datastreamconfig.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.datastreamconfig.Model",
    "NOC.main.handler.LookupField",
  ],
  model: "NOC.main.datastreamconfig.Model",
  search: true,

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          flex: 1,
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          uiStyle: "medium",
          allowBlank: false,
        },
        {
          name: "formats",
          xtype: "gridfield",
          fieldLabel: __("Formats"),
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              width: 150,
              editor: "textfield",
            },
            {
              text: __("Active"),
              dataIndex: "is_active",
              width: 50,
              renderer: NOC.render.Bool,
              editor: "checkbox",
            },
            {
              text: __("Handler"),
              dataIndex: "handler",
              editor: {
                xtype: "main.handler.LookupField",
                query: {
                  allow_ds_filter: true,
                },
              },
              width: 200,
              renderer: NOC.render.Lookup("handler"),
            },
            {
              text: __("Role"),
              dataIndex: "role",
              editor: "textfield",
              flex: 1,
            },
          ],
        },
      ],
    });
    me.callParent();
  },
});