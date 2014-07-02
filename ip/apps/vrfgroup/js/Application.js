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
            text: "Name",
            dataIndex: "name",
            width: 150
        },
        {
            text: "Constraint",
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
            text: "VRFs",
            dataIndex: "vrf_count",
            sortable: false,
            width: 50
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        },
        {
            text: "Tags",
            dataIndex: "tags",
            renderer: "NOC.render.Tags"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "VRF Group",
            allowBlank: false
        },
        {
            name: "address_constraint",
            xtype: "combobox",
            fieldLabel: "Address Constraint",
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
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: "Tags",
            allowBlank: true
        }
    ]
});
