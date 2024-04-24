//---------------------------------------------------------------------
// inv.channel application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.channel.Application");

Ext.define("NOC.inv.channel.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.inv.channel.Model",
    "NOC.inv.channel.EndpointModel",
    "NOC.core.label.LabelField",
    "NOC.project.project.LookupField",
    "NOC.crm.subscriber.LookupField",
    "NOC.crm.supplier.LookupField",
    "NOC.main.remotesystem.LookupField",
  ],
  model: "NOC.inv.channel.Model",
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
          text: __("Free"),
          dataIndex: "is_free",
          render: NOC.render.Bool,
          width: 50,
        },
        {
          text: __("Project"),
          dataIndex: "project",
          width: 200,
          renderer: NOC.render.Lookup("project"),
        },
        {
          text: __("Subscriber"),
          dataIndex: "subscriber",
          width: 200,
          renderer: NOC.render.Lookup("subscriber"),
        },
        {
          text: __("Supplier"),
          dataIndex: "supplier",
          width: 200,
          renderer: NOC.render.Lookup("supplier"),
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
          name: "is_free",
          xtype: "checkbox",
          boxLabel: __("Free"),
        },
        {
          name: "project",
          xtype: "project.project.LookupField",
          fieldLabel: __("Project"),
          allowBlank: true,
        },
        {
          name: "supplier",
          xtype: "crm.supplier.LookupField",
          fieldLabel: __("Supplier"),
          allowBlank: true,
        },
        {
          name: "subscriber",
          xtype: "crm.subscriber.LookupField",
          fieldLabel: __("Subscriber"),
          allowBlank: true,
        },
        {
          name: "labels",
          fieldLabel: __("Labels"),
          xtype: "labelfield",
          allowBlank: true,
          minWidth: 100,
          query: {
            allow_models: ["inv.Channel"],
          },
        },
        /*
        {
          name: "effective_labels",
          xtype: "labeldisplay",
          fieldLabel: __("Effective Labels"),
          allowBlank: true,
        },
        */
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Integration"),
          defaults: {
            padding: 4,
            labelAlign: "top",
          },
          items: [
            {
              name: "remote_system",
              xtype: "main.remotesystem.LookupField",
              fieldLabel: __("Remote System"),
              allowBlank: true,
            },
            {
              name: "remote_id",
              xtype: "textfield",
              fieldLabel: __("Remote ID"),
              allowBlank: true,
              uiStyle: "medium",
            },
            {
              name: "bi_id",
              xtype: "displayfield",
              fieldLabel: __("BI ID"),
              allowBlank: true,
              uiStyle: "medium",
            },
          ],
        },
      ],
      inlines: [
        {
          title: __("Endpoints"),
          model: "NOC.inv.channel.EndpointModel",
          columns: [
            {
              text: __("Tech. Domain"),
              dataIndex: "tech_domain",
              width: 100,
              renderer: NOC.render.Lookup("tech_domain"),
            },
            {
              text: __("Model"),
              dataIndex: "model",
              width: 100,
            },
            {
              text: __("Resource"),
              dataIndex: "resource_id",
              width: 100,
            },
            {
              text: __("Slot"),
              dataIndex: "slot",
              width: 100,
            },
            {
              text: __("Discriminator"),
              dataIndex: "discriminator",
              flex: 1,
            },
          ],
        },
      ],
    });
    me.callParent();
  },
});
