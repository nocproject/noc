//---------------------------------------------------------------------
// main.systemnotification application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.systemnotification.Application");

Ext.define("NOC.main.systemnotification.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.systemnotification.Model",
    "NOC.main.notificationgroup.LookupField",
  ],
  model: "NOC.main.systemnotification.Model",
  search: true,
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      flex: 1,
    },
    {
      text: __("Notification Group"),
      dataIndex: "notification_group",
      renderer: NOC.render.Lookup("notification_group"),
      flex: 1,
    },
  ],
  fields: [
    {
      name: "name",
      xtype: "combobox",
      fieldLabel: __("Name"),
      width: 400,
      allowBlank: false,
      store: [
        "dns.change",
        "dns.domain_expiration_warning",
        "dns.domain_expired",
        "ip.sync_macs",
        "sa.version_inventory",
      ],
    },
    {
      name: "notification_group",
      xtype: "main.notificationgroup.LookupField",
      fieldLabel: __("Notification Group"),
      width: 400,
      allowBlank: true,
    },
  ],
  filters: [
    {
      title: __("By Notify Group"),
      name: "notification_group",
      ftype: "lookup",
      lookup: "main.notificationgroup",
    },
  ],
});
