//---------------------------------------------------------------------
// crm.subscriber application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.subscriber.Application");

Ext.define("NOC.crm.subscriber.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.label.LabelField",
    "NOC.core.StateField",
    "NOC.crm.subscriber.Model",
    "NOC.crm.subscriberprofile.LookupField",
    "NOC.main.remotesystem.LookupField",
    "NOC.project.project.LookupField",
    "NOC.core.IntegrationField",
  ],
  model: "NOC.crm.subscriber.Model",
  search: true,
  rowClassField: "row_class",
  helpId: "reference-subscriber",

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
          text: __("Profile"),
          dataIndex: "profile",
          width: 200,
          renderer: NOC.render.Lookup("profile"),
        },
        {
          text: __("State"),
          dataIndex: "state",
          width: 200,
          renderer: NOC.render.Lookup("state"),
        },
        {
          text: __("Tags"),
          dataIndex: "tags",
          width: 150,
          render: NOC.render.Tags,
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "profile",
          xtype: "crm.subscriberprofile.LookupField",
          fieldLabel: __("Profile"),
          allowBlank: false,
        },
        {
          name: "state",
          xtype: "statefield",
          fieldLabel: __("State"),
          allowBlank: true,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
          uiStyle: "expand",
        },
        {
          name: "address",
          xtype: "textfield",
          fieldLabel: __("Address"),
          allowBlank: true,
          uiStyle: "extra",
        },
        {
          name: "tech_contact_person",
          xtype: "textfield",
          fieldLabel: __("Contact"),
          allowBlank: true,
          uiStyle: "extra",
        },
        {
          name: "tech_contact_phone",
          xtype: "textfield",
          fieldLabel: __("Phone"),
          allowBlank: true,
          uiStyle: "extra",
        },
        {
          name: "project",
          xtype: "project.project.LookupField",
          fieldLabel: __("Project"),
          allowBlank: true,
        },
        {
          xtype: "noc.integrationfield",
        },
        {
          name: "labels",
          xtype: "labelfield",
          fieldLabel: __("Labels"),
          allowBlank: true,
          query: {
            "allow_models": ["crm.Subscriber"],
          },
        },
      ],
    });
    me.callParent();
  },
});
