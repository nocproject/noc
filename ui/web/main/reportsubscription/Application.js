//---------------------------------------------------------------------
// main.reportsubscription application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.reportsubscription.Application");

Ext.define("NOC.main.reportsubscription.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.reportsubscription.Model",
    "NOC.main.notificationgroup.LookupField",
    "NOC.aaa.user.LookupField",
    "NOC.main.ref.report.LookupField",
  ],
  model: "NOC.main.reportsubscription.Model",
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("File Name"),
          dataIndex: "file_name",
          width: 100,
        },
        {
          text: __("Active"),
          dataIndex: "is_active",
          width: 25,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Report"),
          dataIndex: "report",
          width: 250,
          renderer: NOC.render.Lookup("report"),
        },
        {
          text: __("Notification Group"),
          dataIndex: "notification_group",
          flex: 1,
          renderer: NOC.render.Lookup("notification_group"),
        },
      ],

      fields: [
        {
          name: "file_name",
          xtype: "textfield",
          fieldLabel: __("File Name"),
          allowBlank: false,
        },
        {
          name: "is_active",
          xtype: "checkbox",
          boxLabel: __("Is Active"),
        },
        {
          name: "run_as",
          xtype: "aaa.user.LookupField",
          fieldLabel: __("Run As"),
          allowBlank: false,
        },
        {
          name: "report",
          xtype: "main.ref.report.LookupField",
          fieldLabel: __("Report"),
          uiStyle: "medium",
          allowBlank: false,
        },
        {
          name: "subject",
          xtype: "textfield",
          fieldLabel: __("Subject"),
          allowBlank: true,
        },
        {
          name: "notification_group",
          xtype: "main.notificationgroup.LookupField",
          fieldLabel: __("Notification Group"),
          uiStyle: "medium",
          allowBlank: true,
        },
      ],
    });
    me.callParent();
  },
});
