//---------------------------------------------------------------------
// pm.agentprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.agentprofile.Application");

Ext.define("NOC.pm.agentprofile.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.pm.agentprofile.Model",
    "NOC.wf.workflow.LookupField",
  ],
  model: "NOC.pm.agentprofile.Model",
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
          allowBlank: false,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Config"),
          defaults: {
            padding: 4,
          },
          items: [
            {
              name: "zk_check_interval",
              xtype: "numberfield",
              fieldLabel: __("Check Interval"),
              allowBlank: false,
            },
            {
              name: "update_addresses",
              xtype: "checkbox",
              boxLabel: __("Update Addresses"),
            },
          ],
        },
        {
          name: "workflow",
          xtype: "wf.workflow.LookupField",
          fieldLabel: __("Workflow"),
          allowBlank: true,
        },
      ],
    });
    me.callParent();
  },
});