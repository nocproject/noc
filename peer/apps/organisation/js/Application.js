//---------------------------------------------------------------------
// peer.organisation application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.organisation.Application");

Ext.define("NOC.peer.organisation.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.peer.organisation.Model",
        "NOC.peer.maintainer.LookupField"
    ],
    model: "NOC.peer.organisation.Model",
    search: true,
    columns: [
        {
            text: "Organisation",
            dataIndex: "organisation",
            flex: 1
        },

        {
            text: "Org. Name",
            dataIndex: "org_name",
            flex: 1
        },
        {
            text: "Org. Type",
            dataIndex: "org_type",
            flex: 1
        }
    ],
    fields: [
        {
            name: "organisation",
            xtype: "textfield",
            fieldLabel: "Organisation",
            allowBlank: false,
            width: 300
        },
        {
            name: "org_name",
            xtype: "textfield",
            fieldLabel: "Org. Name",
            allowBlank: false,
            width: 300
        },
        {
            name: "org_type",
            xtype: "combobox",
            fieldLabel: "Org. Type",
            allowBlank: false,
            store: ["IANA", "RIR", "NIR", "LIR", "OTHER"]
        },
        {
            name: "address",
            xtype: "textareafield",
            fieldLabel: "Address",
            allowBlank: false,
            anchor: "70%"
        },
        {
            name: "mnt_ref",
            xtype: "peer.maintainer.LookupField",
            fieldLabel: "Mnt. Ref",
            allowBlank: false
        }
    ],
    filters: [
    ]
});
