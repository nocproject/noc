//---------------------------------------------------------------------
// Header
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
Ext.define("NOC.main.desktop.HeaderPanel", {
    extend: "Ext.Panel",
    id: "header",
    region: "north",
    height: 30,
    collapsible: true,
    animCollapse: true,
    split: true,
    preventHeader: true,
    layout: {
        type: "hbox",
        align: "stretch"
    },
    border: false,
    style: {
        backgroundColor: "#417690",
        verticalAlign: "middle"
    },
    items: [
        {
            xtype: "container",
            items: [Ext.create("Ext.Img",{
                src: NOC.settings.logo_url,
                width: NOC.settings.logo_width,
                height: NOC.settings.logo_height
            })],
            border: false,
            style: {
                backgroundColor: "#417690",
                padding: "2 2 2 2"
            }
        },

        {
            xtype: "container",
            html: NOC.settings.installation_name,
            style: {
                fontSize: "18px",
                color: "#f4f379",
                backgroundColor: "#417690",
                paddingLeft: "8px"
            },
            border: false
        },

        {
            xtype: "container",
            flex: 1,
            style: {
                backgroundColor: "#417690"
            }
        },

        {
            xtype: "container",
            html: "Anonymous",
            id: "user_display_name",
            style: {
                backgroundColor: "#417690",
                color: "#f4f379",
                padding: "2 2 2 2"
            }
        },
        
        {
            id: "search",
            xtype: "container",
            style: {
                backgroundColor: "#417690",
                padding: "2 2 2 2"
            },
            items: [
                {
                    xtype: "textfield",
                    emptyText: "Search..."
                }
            ]
        }
    ],
    // Change displayed username
    set_user_name: function(username) {
        Ext.get("user_display_name").dom.innerHTML = username;
        //var u = Ext.getCmp("user_display_name");
    }
});
