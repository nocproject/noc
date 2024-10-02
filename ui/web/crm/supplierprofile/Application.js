//---------------------------------------------------------------------
// crm.supplierprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.supplierprofile.Application");

Ext.define("NOC.crm.supplierprofile.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.label.LabelField",
    "NOC.crm.supplierprofile.Model",
    "NOC.main.style.LookupField",
    "NOC.wf.workflow.LookupField",
    "NOC.main.remotesystem.LookupField",
    "NOC.core.IntegrationField",
  ],
  model: "NOC.crm.supplierprofile.Model",
  search: true,
  rowClassField: "row_class",

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          flex: 1,
        },
        {
          text: __("Workflow"),
          dataIndex: "workflow",
          width: 150,
          renderer: NOC.render.Lookup("workflow"),
        },
        {
          text: __("Labels"),
          dataIndex: "labels",
          width: 150,
          render: NOC.render.LabelField,
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
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
          uiStyle: "expand",
        },
        {
          name: "workflow",
          xtype: "wf.workflow.LookupField",
          fieldLabel: __("Workflow"),
          allowBlank: false,
        },
        {
          name: "style",
          xtype: "main.style.LookupField",
          fieldLabel: __("Style"),
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
            "allow_models": ["crm.SupplierProfile"],
          },
        },
      ],
    });
    me.callParent();
  },
});
