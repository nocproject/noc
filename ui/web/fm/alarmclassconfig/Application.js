//---------------------------------------------------------------------
// fm.alarmclassconfig application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmclassconfig.Application");

Ext.define("NOC.fm.alarmclassconfig.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.fm.alarmclassconfig.Model",
    "NOC.fm.alarmclass.LookupField",
  ],
  model: "NOC.fm.alarmclassconfig.Model",
  columns: [
    {
      text: __("Alarm Class"),
      dataIndex: "alarm_class",
      renderer: NOC.render.Lookup("alarm_class"),
      width: 200,
    },
    {
      text: __("Notification Delay"),
      dataIndex: "notification_delay",
      width: 100,
      align: "right",
    },
    {
      text: __("Control Time 0"),
      dataIndex: "control_time0",
      width: 100,
      align: "right",
    },
    {
      text: __("Control Time 1"),
      dataIndex: "control_time1",
      width: 100,
      align: "right",
    },
    {
      text: __("Control Time N"),
      dataIndex: "control_timeN",
      width: 100,
      align: "right",
    },
  ],
  fields: [
    {
      name: "alarm_class",
      xtype: "fm.alarmclass.LookupField",
      fieldLabel: __("Alarm Class"),
      allowBlank: false,
    },
    {
      name: "notification_delay",
      xtype: "numberfield",
      fieldLabel: __("Notification Delay (s)"),
      allowBlank: true,
      minValue: 0,
    },
    {
      name: "control_time0",
      xtype: "numberfield",
      fieldLabel: __("Control time (no reopens)"),
      allowBlank: true,
      minValue: 0,
    },
    {
      name: "control_time1",
      xtype: "numberfield",
      fieldLabel: __("Control time (1 reopen)"),
      allowBlank: true,
      minValue: 0,
    },
    {
      name: "control_timeN",
      xtype: "numberfield",
      fieldLabel: __("Control time (multiple reopens)"),
      allowBlank: true,
      minValue: 0,
    },
  ],
});
