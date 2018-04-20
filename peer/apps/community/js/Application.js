//---------------------------------------------------------------------
// peer.community application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.community.Application");

Ext.define("NOC.peer.community.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.peer.community.Model",
           "NOC.peer.communitytype.LookupField"
    ],
    model: "NOC.peer.community.Model",
    search: true,
    columns: [
        {
            text: "Community",
            dataIndex: "community",
            flex: 1
        },
        {
            text: "Type",  
            dataIndex: "type",
            renderer: NOC.render.Lookup("type"),
            flex: 1
        },
        {
            text: "Description",  
            dataIndex: "description",
            flex: 1
        }
    ],
    fields: [
        {
            name: "community",
            xtype: "textfield",
            fieldLabel: "Community",
            width: 400,
            allowBlank: false
        },
        {
            name: "type",
            xtype: "peer.communitytype.LookupField",
            fieldLabel: "Type",
            width: 400,
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: "Description",  
            width: 400,
            allowBlank: false
        } 
    ],
    filters: [
        {
            title: "By Community Type",
            name: "type",
            ftype: "lookup",
            lookup: "peer.communitytype"
        }
    ]
});
