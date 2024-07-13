//---------------------------------------------------------------------
// inv.endpoint application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.endpoint.Application");

Ext.define("NOC.inv.endpoint.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.inv.endpoint.Model",
    "NOC.inv.channel.LookupField",
    "NOC.inv.techdomain.LookupField",
    "NOC.core.label.LabelField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.inv.endpoint.Model",
  search: true,
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Channel"),
          dataIndex: "channel",
          width: 200,
          renderer: NOC.render.Lookup("channel"),
        },
        {
          text: __("Resource"),
          dataIndex: "resource",
          width: 100,
          renderer: NOC.render.Lookup("resource"),
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],
      fields: [
        {
          name: "channel",
          xtype: "inv.channel.LookupField",
          fieldLabel: __("Channel"),
        },
        {
          name: "resource",
          xtype: "textfield",
          fieldLabel: __("Resource"),
        },
        {
          name: "is_root",
          xtype: "checkbox",
          fieldLabel: __("Is Root"),
        },
        {
          name: "pair",
          xtype: "numberfield",
          fieldLabel: __("Pair"),
          allowBlank: true,
        },
        {
          name: "used_by",
          xtype: "gridfield",
          columns: [
            {
              text: __("Channel"),
              dataIndex: "channel",
              width: 200,
              renderer: NOC.render.Lookup("channel"),
            },
            {
              text: __("Discrimiator"),
              dataIndex: "discriminator",
              width: 200,
            },
            {
              text: __("Direction"),
              dataIndex: "direction",
              width: 100,
            },
          ],
        },
      ],
    });
    me.callParent();
  },
});
