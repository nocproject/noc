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
            text: __("Name"),
            flex: 1,
            dataIndex: "name"
        },
        {
            text: __("Description"),
            flex: 1,
            dataIndex: "description"
        },
        {
            text: __("Members"),
            flex: 1,
            dataIndex: "members",
            renderer: NOC.render.WrapColumn
        },
        {
            text: __("Tags"),
            flex: 1,
            dataIndex: "tags",
            renderer: "NOC.render.Tags"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("Name"),
            width: 400,
            allowBlank: false,
            plugins: [ 'ucfield' ],
            vtype: "ASSET"
        },
        {
            name: "description",     
            xtype: "textfield",
            fieldLabel: __("Description"),     
            width: 400,
            allowBlank: false
        },
        {
            name: "members",
            xtype: "textareafield",
            fieldLabel: __("members"),
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
            fieldLabel: __("RPSL Header"),
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
            fieldLabel: __("RPSL Footer"),
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
            fieldLabel: __("Tags"),      
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
