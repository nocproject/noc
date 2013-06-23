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
            text: "Person/Role Name",
            dataIndex: "person",
            flex: 1
        },
        {
            text: "Type",
            dataIndex: "type",
            renderer: function(a) {
                return {P: "Person", R: "Role"}[a];
            },
            flex: 1
        },
        {
            text: "RIR",
            dataIndex: "rir",
            renderer: NOC.render.Lookup("rir"),
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
            name: "type",
            xtype: "combobox",
            fieldLabel: "Type",
            allowBlank: false,
            store: [
                ["P", "Person"],
                ["R", "Role"]     
            ]
        },
        {
            name: "person",
            xtype: "textfield",
            fieldLabel: "Person/Role Name",
            allowBlank: false,
            anchor: "70%"
        },
        {
            name: "address",
            xtype: "textareafield",
            fieldLabel: "Address",
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
    ],
    preview: {
        xtype: "NOC.core.RepoPreview",
        syntax: "rpsl",
        previewName: "Person RPSL: {{nic_hdl}}",
        restUrl: "/peer/person/{{id}}/repo/rpsl/"
    }
});
