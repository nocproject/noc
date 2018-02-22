//---------------------------------------------------------------------
// ip.vrfgroup application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.vrfgroup.Application");

Ext.define("NOC.ip.vrfgroup.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.ip.vrfgroup.Model"
    ],
    model: "NOC.ip.vrfgroup.Model",
    search: true,
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 150
        },
        {
            text: __("Constraint"),
            dataIndex: "address_constraint",
            width: 100,
            renderer: function(value) {
                if(value == "V")
                    return "Unique per VRF";
                else
                    return "Unique per Group";
            }
        },
        {
            text: __("VRFs"),
            dataIndex: "vrf_count",
            sortable: false,
            width: 50
        },
        {
            text: __("Description"),
            dataIndex: "description",
            flex: 1
        },
        {
            text: __("Tags"),
            dataIndex: "tags",
            renderer: "NOC.render.Tags"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("VRF Group"),
            allowBlank: false,
            uiStyle: "medium"
        },
        {
            name: "address_constraint",
            xtype: "combobox",
            fieldLabel: __("Address Constraint"),
            allowBlank: false,
            queryMode: "local",
            displayField: "label",
            valueField: "id",
            store: {
                fields: ["id", "label"],
                data: [
                    {id: "V", label: "Unique per VRF"},
                    {id: "G", label: "Unique per Group"}
                ]
            }
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: __("Tags"),
            allowBlank: true
        }
    ]
});
