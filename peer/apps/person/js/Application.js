//---------------------------------------------------------------------
// peer.person application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.person.Application");

Ext.define("NOC.peer.person.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.peer.person.Model",
        "NOC.peer.rir.LookupField"
    ],
    model: "NOC.peer.person.Model",
    search: true,
    columns: [
        {
            text: "Nic-hdl",
            dataIndex: "nic_hdl",
            flex: 1
        },

        {
            text: "Person",
            dataIndex: "person",
            flex: 1
        },
        {
            text: "RIR",
            dataIndex: "rir__label",
            flex: 1
        }
    ],
    fields: [
        {
            name: "nic_hdl",
            xtype: "textfield",
            fieldLabel: "Nic-hdl",
            allowBlank: false,
            anchor: "70%"
        },
        {
            name: "person",
            xtype: "textfield",
            fieldLabel: "person",
            allowBlank: false,
            anchor: "70%"
        },
        {
            name: "address",
            xtype: "textareafield",
            fieldLabel: "address",
            allowBlank: false,
            anchor: "70%"
        },
        {
            name: "phone",
            xtype: "textareafield",
            fieldLabel: "Phone",
            allowBlank: false,
            anchor: "70%"
        },
        {
            name: "fax_no",
            xtype: "textareafield",
            fieldLabel: "Fax-no",
            anchor: "70%"
        },
        {
            name: "email",
            xtype: "textareafield",
            fieldLabel: "Email",
            allowBlank: false,
            anchor: "70%"
        },
        {
            name: "rir",
            xtype: "peer.rir.LookupField",
            fieldLabel: "RIR",
            allowBlank: false
        },
        {
            name: "extra",
            xtype: "textareafield",
            fieldLabel: "Extra",
            anchor: "70%"
        }
    ],
    filters: [
        {
            title: "By RIR",
            name: "rir",
            ftype: "lookup",
            lookup: "peer.rir"
        }
    ]
});
