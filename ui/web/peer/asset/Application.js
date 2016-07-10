//---------------------------------------------------------------------
// peer.asset application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.asset.Application");

Ext.define("NOC.peer.asset.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.peer.asset.Model",
        "Ext.ux.form.UCField"
    ],
    model: "NOC.peer.asset.Model",
    search: true,
    columns: [
        {
            text: "Name",
            flex: 1,
            dataIndex: "name"
        },
        {
            text: "Description",
            flex: 1,
            dataIndex: "description"
        },
        {
            text: "Members",
            flex: 1,
            dataIndex: "members",
            renderer: NOC.render.WrapColumn
        },
        {
            text: "Tags",
            flex: 1,
            dataIndex: "tags",
            renderer: "NOC.render.Tags"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "Name",
            width: 400,
            allowBlank: false,
            plugins: [ 'ucfield' ],
            vtype: "ASSET"
        },
        {
            name: "description",     
            xtype: "textfield",
            fieldLabel: "Description",     
            width: 400,
            allowBlank: false
        },
        {
            name: "members",
            xtype: "textareafield",
            fieldLabel: "members",
            allowBlank: true,
            width: 600,
            height: 100,
            plugins: [ 'ucfield' ],
            vtype: "ASorASSET",
            fieldStyle: {
                fontFamily: "Courier"
            }
        },
        {
            name: "rpsl_header",
            xtype: "textareafield",
            fieldLabel: "RPSL Header",
            allowBlank: true,
            width: 600,
            height: 100,
            fieldStyle: {
                fontFamily: "Courier"
            }
        },
        {
            name: "rpsl_footer",
            xtype: "textareafield",
            fieldLabel: "RPSL Footer",
            allowBlank: true,
            width: 600,
            height: 100,
            fieldStyle: {
                fontFamily: "Courier"
            }
        },
        { 
            name: "tags",      
            xtype: "tagsfield",   
            fieldLabel: "Tags",      
            width: 400,     
            allowBlank: true
        }
//    ],
//    actions: [
//        {
//            title: "RPSL",
//            action: "rpsl"
//        }
    ]
});
