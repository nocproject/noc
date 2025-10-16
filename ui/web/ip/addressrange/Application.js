//---------------------------------------------------------------------
// ip.addressrange application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.addressrange.Application");

Ext.define("NOC.ip.addressrange.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.label.LabelField",
    "NOC.ip.addressrange.Model",
    "NOC.ip.vrf.LookupField",
  ],
  model: "NOC.ip.addressrange.Model",
  search: true,
  rowClassField: "row_class",
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      flex: 1,
    },
    {
      dataIndex: "is_active",
      text: __("Active?"),
      renderer: NOC.render.Bool,
      width: 50,
    },
    {
      text: __("VRF"),
      dataIndex: "vrf",
      renderer: NOC.render.Lookup("vrf"),
    },
    {
      text: __("AFI"),
      dataIndex: "afi",
      width: 40,
      renderer: function(v){
        return "IPv" + v;
      },
    },
    {
      text: __("From Address"),
      dataIndex: "from_address",
      width: 80,
    },
    {
      text: __("To Address"), 
      dataIndex: "to_address",
      width: 80,
    },
    {
      dataIndex: "is_locked",
      text: __("Locked?"),
      renderer: NOC.render.Bool,
      width: 50,
    },
    {
      text: __("Action"),
      dataIndex: "action",
      renderer: function(a){
        return {N: "Do nothing", G: "Generate FQDNs", D: "Partial reverse zone delegation"}[a];
      },
    },
    {
      text: __("Description"),
      dataIndex: "description",
    },
    {
      text: __("Labels"),
      dataIndex: "labels",
      renderer: NOC.render.LabelField,
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
      name: "is_active",
      xtype: "checkboxfield",
      boxLabel: __("Is Active"),
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
      store: [["4", "IPv4"], ["6", "IPv6"]],
      uiStyle: "small",
    },
    {
      name: "from_address",
      xtype: "textfield",
      fieldLabel: __("From Address"),
      allowBlank: false,
      uiStyle: "medium",
    },
    {
      name: "to_address",
      xtype: "textfield",
      fieldLabel: __("To Address"),
      allowBlank: false,
      uiStyle: "medium",
    },
    {
      name: "description",
      xtype: "textareafield",
      fieldLabel: __("Description"),
      allowBlank: false,
      anchor: "70%",
    },
    {
      name: "is_locked",
      xtype: "checkboxfield",
      boxLabel: __("Is Locked"),
    },
    {
      name: "action",
      xtype: "combobox",
      fieldLabel: __("Action"),
      allowBlank: false,
      store: [
        ["N", "Do nothing"],
        ["G", "Generate FQDNs"],
        ["D", "Partial reverse zone delegation"],
      ],
      uiStyle: "medium",
    },
    {
      name: "fqdn_template",
      xtype: "textfield",
      allowBlank: true,
      fieldLabel: __("FQDN Template"),
    },
    {
      name: "reverse_nses",
      xtype: "textfield",
      allowBlank: true,
      fieldLabel: __("Reverse NSes"),
    },
    {
      name: "labels",
      xtype: "labelfield",
      fieldLabel: __("Labels"),
      allowBlank: true,
      query: {
        "enable_ipaddressrange": true,
      },
    },
    {
      name: "tt",
      xtype: "textfield",
      regexText: /^\d*$/,
      fieldLabel: __("TT"),
      allowBlank: true,
    },
    {
      name: "allocated_till",
      xtype: "datefield",
      startDay: 1,
      fieldLabel: __("Allocated till"),
      allowBlank: true,
    },
  ],
  filters: [
    {
      title: __("By Is Active"),
      name: "is_active",
      ftype: "boolean",
    },
    {  
      title: __("By VRF"),
      name: "vrf",   
      ftype: "lookup",
      lookup: "ip.vrf",
    },
    {  
      title: __("By Is Locked"),
      name: "is_locked",   
      ftype: "boolean",
    },
  ],
  showOpError: function(action, op, status){
    var me = this;
    // Detect Syntax Errors
    if(status.traceback){
      NOC.error(status.traceback);
      return;
    }
    me.callParent([action, op, status]);
  },
});
