//---------------------------------------------------------------------
// peer.peerprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.peerprofile.Application");

Ext.define("NOC.peer.peerprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.peer.peerprofile.Model",
        "NOC.wf.workflow.LookupField"
    ],
    model: "NOC.peer.peerprofile.Model",
    search: true,
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            flex: 1
        },
        {
            text: __("Description"),
            dataIndex: "description",
            flex: 1
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("Name"),
            allowBlank: false,
            width: 300
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: __("Description"),
            allowBlank: false,
            width: 300
        },
        {
            name: "workflow",
            xtype: "wf.workflow.LookupField",
            fieldLabel: __("WorkFlow"),
            allowBlank: true
        },
        {
            name: "max_prefixes",
            xtype: "textfield",
            maskRe: /\d/i,
            fieldLabel: __("Max. Prefixes"),
            allowBlank: false
        }
    ],
    filters: [
    ]
});
