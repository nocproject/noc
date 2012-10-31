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
        "NOC.main.ref.profile.LookupField"
    ],
    model: "NOC.peer.peeringpoint.Model",
    search: true,
    columns: [
        {
            text: "FQDN",
            flex: 1,
            dataIndex: "hostname"
        },
        {
            text: "Location",
            flex: 1,
            dataIndex: "location"
        },
        {
            text: "Local AS",
            flex: 1,
            dataIndex: "local_as__label"
        },
        {
            text: "Router-ID",
            flex: 1,
            dataIndex: "router_id"
        },
        {
            text: "Profile",
            flex: 1,
            dataIndex: "profile_name"
        },
        {
            text: "Import Communities",
            flex: 1,
            dataIndex: "communities"
        }
    ],
    fields: [
        {
            name: "hostname",
            xtype: "textfield",
            fieldLabel: "FQDN",
            allowBlank: false
        },
        {
            name: "location",
            xtype: "textfield",
            fieldLabel: "Location"
        },
        {
            name: "local_as",
            xtype: "peer.as.LookupField",
            fieldLabel: "Local AS",
            allowBlank: false
        },
        {
            name: "router_id",
            xtype: "textfield",
            fieldLabel: "Router-ID",
            allowBlank: false
        },
        {
            name: "profile_name",
            xtype: "main.ref.profile.LookupField",
            fieldLabel: "Profile",
            allowBlank: false
        },
        {
            name: "communities",
            xtype: "textfield",
            fieldLabel: "Import Communities"
        },
        {
            name: "enable_prefix_list_provisioning",
            xtype: "checkboxfield",
            boxLabel: "Enable Prefix-List Provisioning"
        },
        {
            name: "prefix_list_notification_group",
            xtype: "main.notificationgroup.LookupField",
            fieldLabel: "Prefix-List Notification Group"
        }
    ],
    filters: [
        {
            title: "By Profile",
            name: "profile_name",
            ftype: "lookup",
            lookup: "main.ref.profile"
        }
    ]
});
