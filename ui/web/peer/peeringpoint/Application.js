//---------------------------------------------------------------------
// peer.peeringpoint application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.peeringpoint.Application");

Ext.define("NOC.peer.peeringpoint.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.peer.peeringpoint.Model",
    "NOC.peer.as.LookupField",
    "NOC.main.notificationgroup.LookupField",
    "NOC.sa.profile.LookupField",
  ],
  model: "NOC.peer.peeringpoint.Model",
  search: true,
  columns: [
    {
      text: __("FQDN"),
      flex: 1,
      dataIndex: "hostname",
    },
    {
      text: __("Location"),
      flex: 1,
      dataIndex: "location",
    },
    {
      text: __("Local AS"),
      flex: 1,
      dataIndex: "local_as",
      renderer: NOC.render.Lookup("local_as"),
    },
    {
      text: __("Router-ID"),
      flex: 1,
      dataIndex: "router_id",
    },
    {
      text: __("Profile"),
      flex: 1,
      dataIndex: "profile",
      renderer: NOC.render.Lookup("profile"),
    },
    {
      text: __("Import Communities"),
      flex: 1,
      dataIndex: "communities",
    },
  ],
  fields: [
    {
      name: "hostname",
      xtype: "textfield",
      fieldLabel: __("FQDN"),
      allowBlank: false,
    },
    {
      name: "location",
      xtype: "textfield",
      fieldLabel: __("Location"),
    },
    {
      name: "local_as",
      xtype: "peer.as.LookupField",
      fieldLabel: __("Local AS"),
      allowBlank: false,
    },
    {
      name: "router_id",
      xtype: "textfield",
      fieldLabel: __("Router-ID"),
      allowBlank: false,
    },
    {
      name: "profile",
      xtype: "sa.profile.LookupField",
      fieldLabel: __("Profile"),
      allowBlank: false,
    },
    {
      name: "communities",
      xtype: "textfield",
      fieldLabel: __("Import Communities"),
    },
    {
      name: "enable_prefix_list_provisioning",
      xtype: "checkboxfield",
      boxLabel: __("Enable Prefix-List Provisioning"),
    },
    {
      name: "prefix_list_notification_group",
      xtype: "main.notificationgroup.LookupField",
      fieldLabel: __("Prefix-List Notification Group"),
    },
  ],
  filters: [
    {
      title: "By Profile",
      name: "profile_name",
      ftype: "lookup",
      lookup: "sa.profile",
    },
  ],
});
