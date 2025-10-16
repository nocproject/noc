//---------------------------------------------------------------------
// sa.objectnotification application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.objectnotification.Application");

Ext.define("NOC.sa.objectnotification.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.sa.objectnotification.Model",
    "NOC.main.notificationgroup.LookupField",
    "NOC.core.combotree.ComboTree",
  ],
  model: "NOC.sa.objectnotification.Model",
  columns: [
    {
      text: __("Resource Group"),
      dataIndex: "resource_group",
      renderer: NOC.render.Lookup("resource_group"),
      width: 200,
    },
    {
      text: __("Notification"),
      dataIndex: "notification_group",
      renderer: NOC.render.Lookup("notification_group"),
      width: 200,
    },
    {
      text: __("Config Changed"),
      dataIndex: "config_changed",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Alarm Risen"),
      dataIndex: "alarm_risen",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Alarm Reopened"),
      dataIndex: "alarm_reopened",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Alarm Cleared"),
      dataIndex: "alarm_cleared",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Alarm Commented"),
      dataIndex: "alarm_commented",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("New"),
      dataIndex: "new",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Deleted"),
      dataIndex: "deleted",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Version Changed"),
      dataIndex: "version_changed",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Script Failed"),
      dataIndex: "script_failed",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Config Policy Violation"),
      dataIndex: "config_policy_violation",
      width: 50,
      renderer: NOC.render.Bool,
    },
  ],
  fields: [
    {
      name: "resource_group",
      xtype: "noc.core.combotree",
      restUrl: "/inv/resourcegroup/",
      fieldLabel: __("Resource Group"),
      listWidth: 1,
      listAlign: "left",
      labelAlign: "left",
      width: 500,
      allowBlank: false,
    },
    {
      name: "notification_group",
      xtype: "main.notificationgroup.LookupField",
      fieldLabel: __("Notification Group"),
      allowBlank: false,
    },
    {
      name: "config_changed",
      xtype: "checkboxfield",
      boxLabel: __("Config changed"),
    },
    {
      name: "alarm_risen",
      xtype: "checkboxfield",
      boxLabel: __("Alarm risen"),
    },
    {
      name: "alarm_reopened",
      xtype: "checkboxfield",
      boxLabel: __("Alarm reopened"),
    },
    {
      name: "alarm_cleared",
      xtype: "checkboxfield",
      boxLabel: __("Alarm cleared"),
    },
    {
      name: "alarm_commented",
      xtype: "checkboxfield",
      boxLabel: __("Alarm commented"),
    },
    {
      name: "new",
      xtype: "checkboxfield",
      boxLabel: __("New"),
    },
    {
      name: "deleted",
      xtype: "checkboxfield",
      boxLabel: __("Deleted"),
    },
    {
      name: "version_changed",
      xtype: "checkboxfield",
      boxLabel: __("Version changed"),
    },
    {
      name: "interface_changed",
      xtype: "checkboxfield",
      boxLabel: __("Interface changed"),
    },
    {
      name: "script_failed",
      xtype: "checkboxfield",
      boxLabel: __("Script failed"),
    },
    {
      name: "config_policy_violation",
      xtype: "checkboxfield",
      boxLabel: __("Config policy violation"),
    },
  ],
});
