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
        "NOC.wf.workflow.LookupField",
        "Ext.ux.form.GridField"
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
            labelWidth: 200,
            width: 300
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: __("Description"),
            allowBlank: false,
            width: 300,
            labelWidth: 200,
            uiStyle: "medium"
        },
        {
            name: "workflow",
            xtype: "wf.workflow.LookupField",
            fieldLabel: __("WorkFlow"),
            allowBlank: true,
            labelWidth: 200,
            uiStyle: "medium"
        },
        {
            name: "max_prefixes",
            xtype: "textfield",
            maskRe: /\d/i,
            fieldLabel: __("Max. Prefixes"),
            allowBlank: false,
            labelWidth: 200,
            uiStyle: "medium"
        },
        {
            name: "status_discovery",
            xtype: "combobox",
            fieldLabel: __("Status Discovery"),
            allowBlank: true,
            labelWidth: 200,
            defaultValue: "d",
            store: [
                ["d", __("Disabled")],
                ["e", __("Enable")],
                ["c", __("Clear Alarm")],
                ["ca", __("Clear Alarm if Admin Down")],
                ["rc", __("Raise & Clear Alarm")]
            ],
            uiStyle: "medium"
        },
        {
            name: "status_change_notification",
            xtype: "combobox",
            fieldLabel: __("Status Change Notification"),
            allowBlank: true,
            labelWidth: 200,
            defaultValue: "d",
            store: [
                ["d", __("Disabled")],
                ["c", __("Only Changed")],
                ["a", __("All Message")],
            ],
            uiStyle: "medium"
        },
        {
            name: "data",
            xtype: "gridfield",
            fieldLabel: __("Peer Data"),
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150,
                    editor: "textfield"
                },
                {
                    text: __("Value"),
                    dataIndex: "value",
                    width: 150,
                    editor: "textfield"
                }
            ]
        }
    ],
    filters: [
    ]
});
