//---------------------------------------------------------------------
// fm.alarmescalation application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmescalation.Application");

Ext.define("NOC.fm.alarmescalation.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.fm.alarmescalation.Model",
    "NOC.sa.administrativedomain.LookupField",
    "NOC.fm.alarmclass.LookupField",
    "NOC.fm.ttsystem.LookupField",
    "NOC.main.template.LookupField",
    "NOC.main.notificationgroup.LookupField",
    "NOC.main.timepattern.LookupField",
    "NOC.inv.resourcegroup.LookupField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.fm.alarmescalation.Model",
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
          name: "global_limit",
          xtype: "numberfield",
          fieldLabel: __("Global limit"),
          allowBlank: true,
          uiStyle: "small",
        },
        {
          name: "max_escalation_retries",
          xtype: "numberfield",
          fieldLabel: __("Escalation Retries"),
          allowBlank: false,
          min: 0,
          uiStyle: "small",
        },
        {
          name: "alarm_classes",
          xtype: "gridfield",
          fieldLabel: __("Alarm Classes"),
          columns: [
            {
              text: __("Alarm Class"),
              dataIndex: "alarm_class",
              editor: "fm.alarmclass.LookupField",
              renderer: NOC.render.Lookup("alarm_class"),
              flex: 1,
            },
          ],
        },
        {
          name: "pre_reasons",
          xtype: "gridfield",
          fieldLabel: __("Pre Reasons"),
          columns: [
            {
              text: __("TT System"),
              dataIndex: "tt_system",
              editor: "fm.ttsystem.LookupField",
              renderer: NOC.render.Lookup("tt_system"),
              width: 150,
            },
            {
              text: __("Pre Reason"),
              dataIndex: "pre_reason",
              editor: "textfield",
              flex: 1,
            },
          ],
        },
        {
          name: "escalations",
          xtype: "gridfield",
          fieldLabel: __("Escalations"),
          columns: [
            {
              text: __("Delay"),
              dataIndex: "delay",
              editor: "numberfield",
              width: 75,
            },
            {
              text: __("Adm. domain"),
              dataIndex: "administrative_domain",
              editor: "sa.administrativedomain.LookupField",
              width: 150,
              renderer: NOC.render.Lookup("administrative_domain"),
            },
            {
              text: __("Resource Group"),
              dataIndex: "resource_group",
              editor: "inv.resourcegroup.LookupField",
              width: 150,
              renderer: NOC.render.Lookup("resource_group"),
            },
            {
              text: __("Time Pattern"),
              dataIndex: "time_pattern",
              editor: "main.timepattern.LookupField",
              renderer: NOC.render.Lookup("time_pattern"),
            },
            {
              text: __("Severity"),
              dataIndex: "min_severity",
              editor: "numberfield",
              width: 70,
            },
            {
              text: __("Notification Group"),
              dataIndex: "notification_group",
              editor: "main.notificationgroup.LookupField",
              width: 150,
              renderer: NOC.render.Lookup("notification_group"),
            },
            {
              text: __("Open Template"),
              dataIndex: "template",
              editor: "main.template.LookupField",
              width: 100,
              renderer: NOC.render.Lookup("template"),
            },
            {
              text: __("Clear Template"),
              dataIndex: "clear_template",
              editor: "main.template.LookupField",
              width: 100,
              renderer: NOC.render.Lookup("clear_template"),
            },
            {
              text: __("TT"),
              dataIndex: "create_tt",
              editor: "checkboxfield",
              width: 50,
              renderer: NOC.render.Bool,
            },
            {
              text: __("GTT"),
              dataIndex: "promote_group_tt",
              editor: "checkboxfield",
              width: 50,
              renderer: NOC.render.Bool,
            },
            {
              text: __("ATT"),
              dataIndex: "promote_affected_tt",
              editor: "checkboxfield",
              width: 50,
              renderer: NOC.render.Bool,
            },
            {
              text: __("Wait TT"),
              dataIndex: "wait_tt",
              editor: "checkboxfield",
              width: 50,
              renderer: NOC.render.Bool,
            },
            {
              text: __("Close TT"),
              dataIndex: "close_tt",
              editor: "checkboxfield",
              width: 50,
              renderer: NOC.render.Bool,
            },
            {
              text: __("Stop"),
              dataIndex: "stop_processing",
              editor: "checkboxfield",
              width: 50,
              renderer: NOC.render.Bool,
            },
          ],
        },
      ],
    });
    me.callParent();
  },
});
