//---------------------------------------------------------------------
// dns.dnsserver application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnsserver.Application");

Ext.define("NOC.dns.dnsserver.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.dns.dnsserver.Model",
    "NOC.main.sync.LookupField",
  ],
  model: "NOC.dns.dnsserver.Model",
  search: true,
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      width: 100,
    },
    {
      text: __("IP"),
      dataIndex: "ip",
      width: 100,
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
      allowBlank: false,
    },
    {
      name: "ip",
      xtype: "textfield",
      fieldLabel: __("IP"),
      allowBlank: true,
    },
    {
      name: "description",
      xtype: "textfield",
      fieldLabel: __("Description"),
      allowBlank: true,
    },
  ],
});
