//---------------------------------------------------------------------
// dns.dnszoneprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnszoneprofile.Application");

Ext.define("NOC.dns.dnszoneprofile.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.dns.dnszoneprofile.Model",
    "NOC.dns.dnsserver.LookupField",
    "NOC.dns.dnsserver.M2MField",
    "NOC.main.notificationgroup.LookupField",
  ],
  model: "NOC.dns.dnszoneprofile.Model",
  search: true,
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      flex: 1,
    },
    {
      text: __("TTL"),
      dataIndex: "zone_ttl",
      flex: 1,
    },
    {
      text: __("Notification Group"),
      dataIndex: "notification_group",
      renderer: NOC.render.Lookup("notification_group"),
      flex: 1,
    },
    {
      text: __("Masters"),
      dataIndex: "masterslabel",
      flex: 1,
    },
    {
      text: __("Slaves"),
      dataIndex: "slaveslabel",
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
      xtype: "dns.dnsserver.M2MField",
      name: "masters",
      fieldLabel: __("Masters"),
      allowBlank: true,
    },
    {
      xtype: "dns.dnsserver.M2MField",
      name: "slaves",
      fieldLabel: __("Slaves"),
      allowBlank: true,
    },
    {
      name: "zone_soa",
      xtype: "textfield",
      fieldLabel: __("SOA"),
      width: 300,
      allowBlank: false,
    },
    {
      name: "zone_contact",   
      xtype: "textfield",
      fieldLabel: __("Contact"),
      width: 300,
      allowBlank: false,
    },
    {
      name: "zone_refresh",
      xtype: "numberfield",
      fieldLabel: __("Refresh"),
      hideTrigger: true,
      width: 160,
      keyNavEnabled: false,
      mouseWheelEnabled: false,
      allowBlank: false,
    },
    {
      name: "zone_retry",
      xtype: "numberfield",
      fieldLabel: __("Retry"),     
      hideTrigger: true,
      width: 160,                    
      keyNavEnabled: false,        
      mouseWheelEnabled: false,        
      allowBlank: false,
    },
    {
      name: "zone_expire",
      xtype: "numberfield",
      fieldLabel: __("Expire"),     
      hideTrigger: true,
      width: 160,                    
      keyNavEnabled: false,        
      mouseWheelEnabled: false,        
      allowBlank: false,
    },
    {
      name: "zone_ttl",
      xtype: "numberfield",
      fieldLabel: __("TTL"),     
      hideTrigger: true,
      width: 160,                    
      keyNavEnabled: false,        
      mouseWheelEnabled: false,        
      allowBlank: false,
    },
    {
      name: "notification_group",
      xtype: "main.notificationgroup.LookupField",
      fieldLabel: __("Notification Group"),
      allowBlank: true,
    },
    {
      name: "description",
      xtype: "textareafield",
      fieldLabel: __("Description"),
      allowBlank: true,      
      width: 600, 
      height: 100,
      fieldStyle: {
        fontFamily: "Courier",
      },
    },
  ],
});
