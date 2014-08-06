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
        "NOC.dns.dnsserver.M2MField",
        "NOC.main.notificationgroup.LookupField"
    ],
    model: "NOC.dns.dnszoneprofile.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            flex: 1
        },
        {
            text: "TTL",
            dataIndex: "zone_ttl",
            flex: 1
        },
        {
            text: "Notification Group",
            dataIndex: "notification_group",
            renderer: NOC.render.Lookup("notification_group"),
            flex: 1
        },
        {
            text: "Masters",
            dataIndex: "masterslabel",
            flex: 1
        },
        {
            text: "Slaves",
            dataIndex: "slaveslabel",
            flex: 1
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "Name",
            allowBlank: false
        },
        {
            xtype: "dns.dnsserver.M2MField",
            name: "masters",
            fieldLabel: "Masters",
            allowBlank: true
        },
        {
            xtype: "dns.dnsserver.M2MField",
            name: "slaves",
            fieldLabel: "Slaves",
            allowBlank: true
        },
        {
            name: "zone_soa",
            xtype: "textfield",
            fieldLabel: "SOA",
            width: 300,
            allowBlank: false
        },
        {
            name: "zone_contact",   
            xtype: "textfield",
            fieldLabel: "Contact",
            width: 300,
            allowBlank: false
        },
        {
            name: "zone_refresh",
            xtype: "numberfield",
            fieldLabel: "Refresh",
            hideTrigger: true,
            width: 160,
            keyNavEnabled: false,
            mouseWheelEnabled: false,
            allowBlank: false
        },
        {
            name: "zone_retry",
            xtype: "numberfield",
            fieldLabel: "Retry",     
            hideTrigger: true,
            width: 160,                    
            keyNavEnabled: false,        
            mouseWheelEnabled: false,        
            allowBlank: false
        },
        {
            name: "zone_expire",
            xtype: "numberfield",
            fieldLabel: "Expire",     
            hideTrigger: true,
            width: 160,                    
            keyNavEnabled: false,        
            mouseWheelEnabled: false,        
            allowBlank: false
        },
        {
            name: "zone_ttl",
            xtype: "numberfield",
            fieldLabel: "TTL",     
            hideTrigger: true,
            width: 160,                    
            keyNavEnabled: false,        
            mouseWheelEnabled: false,        
            allowBlank: false
        },
        {
            name: "notification_group",
            xtype: "main.notificationgroup.LookupField",
            fieldLabel: "Notification Group",
            allowBlank: true
        },
        {
            name: "description",
            xtype: "textareafield",
            fieldLabel: "Description",
            allowBlank: true,      
            width: 600, 
            height: 100,
            fieldStyle: {
                fontFamily: "Courier"
            }
        }
    ]
});
