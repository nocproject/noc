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
  ],
  model: "NOC.inv.endpoint.Model",
  search: true,
  initComponent: function () {
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Channel"),
          dataIndex: "channel",
          width: 200,
          renderer: NOC.render.Lookup("channel"),
        },
        {
          text: __("Tech. Domain"),
          dataIndex: "tech_domain",
          width: 100,
          renderer: NOC.render.Lookup("tech_domain"),
        },
        // @todo: model + resource
        {
          text: __("Slot"),
          dataIndex: "slot",
          width: 100,
        },
        {
          text: __("Discriminator"),
          dataIndex: "discriminator",
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
          uiStyle: "medium",
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          uiStyle: "medium",
        },
        {
          name: "channel",
          xtype: "inv.channel.LookupField",
          fieldLabel: __("Channel"),
        },
        {
          name: "tech_domain",
          xtype: "inv.techdomain.LookupField",
          fieldLabel: __("Tech. Domain"),
        },
        {
          xtype: "fieldset",
          title: __("Resource"),
          layout: "hbox",
          defaults: {
            padding: 4,
            labelAlign: "top",
          },
          items: [
            {
              name: "model",
              xtype: "combobox",
              fieldLabel: __("Model"),
              store: [["inv.Object", "Object"]],
            },
            {
              name: "resource_id",
              xtype: "textfield",
              fieldLabel: __("Resource"),
              uiStyle: "medium",
            },
            {
              name: "slot",
              xtype: "textfield",
              fieldLabel: __("Slot"),
              uiStyle: "medium",
              allowBlank: true,
            },
            {
              name: "discriminator",
              xtype: "textfield",
              fieldLabel: __("Discriminator"),
              uiStyle: "medium",
              allowBlank: true,
            },
          ],
        },
        {
          name: "labels",
          fieldLabel: __("Labels"),
          xtype: "labelfield",
          allowBlank: true,
          minWidth: 100,
          query: {
            allow_models: ["inv.Enpoint"],
          },
        },
      ],
    });
    me.callParent();
  },
});
