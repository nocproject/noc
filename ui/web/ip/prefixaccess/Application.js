//---------------------------------------------------------------------
// ip.prefixaccess application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefixaccess.Application");

Ext.define("NOC.ip.prefixaccess.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.ip.prefixaccess.Model",
    "NOC.aaa.user.LookupField",
    "NOC.ip.vrf.LookupField",
  ],
  model: "NOC.ip.prefixaccess.Model",
  search: true,
  columns: [
    {
      text: __("User"),
      dataIndex: "user",
      renderer: NOC.render.Lookup("user"),
    },
    {
      text: __("VRF"),
      dataIndex: "vrf",
      renderer: NOC.render.Lookup("vrf"),
    },
    {
      text: __("AFI"),
      dataIndex: "afi",
      renderer: function(v){ return "IPv" + v; },
    },
    {
      text: __("Prefix"),
      dataIndex: "prefix",
    },
    {
      text: __("View"),
      dataIndex: "can_view",
      renderer: NOC.render.Bool,
      width: 50,
    },
    {
      text: __("Change"),
      dataIndex: "can_change",
      renderer: NOC.render.Bool,
      width: 50,
    },
  ],
  fields: [
    {
      name: "user",
      xtype: "aaa.user.LookupField",
      fieldLabel: __("User"),
      allowBlank: false,
    },
    {
      name: "vrf",
      xtype: "ip.vrf.LookupField",
      fieldLabel: __("VRF"),
      allowBlank: false,
    },
    {
      name: "afi",
      xtype: "combobox",
      fieldLabel: __("Address Family"),
      allowBlank: false,
      queryMode: "local",
      displayField: "label",
      valueField: "id",
      store: {
        fields: ["id", "label"],
        data: [
          {id: "4", label: "IPv4"},
          {id: "6", label: "IPv6"},
        ],
      },
    },
    {
      name: "prefix",
      xtype: "textfield",
      fieldLabel: __("Prefix"),
      allowBlank: false,
    },
    {
      name: "can_view",
      xtype: "checkboxfield",
      boxLabel: __("Can View"),
      allowBlank: false,
    },
    {
      name: "can_change",
      xtype: "checkboxfield",
      boxLabel: __("Can Change"),
      allowBlank: false,
    },
  ],
  filters: [
    {
      title: __("By User"),
      name: "user",
      ftype: "lookup",
      lookup: "aaa.user",
    },
    {
      title: __("By VRF"),
      name: "vrf",
      ftype: "lookup",
      lookup: "ip.vrf",
    },
    {
      title: __("By AFI"),
      name: "afi",
      ftype: "afi",
    },
    {
      title: __("By Can View"),
      name: "can_view",
      ftype: "boolean",
    },
    {
      title: __("By Can Change"),
      name: "can_change",
      ftype: "boolean",
    },
  ],
});
