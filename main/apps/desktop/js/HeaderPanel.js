//---------------------------------------------------------------------
// Header
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.HeaderPanel");

Ext.define("NOC.main.desktop.HeaderPanel", {
    extend: "Ext.Panel",
    id: "header",
    region: "north",
    height: 30,
    maxHeight: 30,
    minHeight: 30,
    collapsible: true,
    animCollapse: true,
    collapseMode: "mini",
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

        /*
        {
            xtype: "container",
            html: "Anonymous",
            id: "user_display_name",
            style: {
                backgroundColor: "#417690",
                color: "#f4f379",
                padding: "2 2 2 2"
            }
        },*/
        Ext.create("Ext.Button", {
            id: "user_display_name",
            text: "Anonymous",
            scale: "small",
            menu: [
                {
                    id: "header_menu_toggle",
                    text: "Collapse all panels"
                },
                {
                    id: "header_menu_profile",
                    text: "User profile ...",
                    disabled: true
                },
                {
                    id: "header_menu_logout",
                    text: "Logout"
                }
            ]
        }),
        
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
                    emptyText: "Search...",
                    inputType: "search"
                }
            ]
        }
    ],
    // Change displayed username
    set_user_name: function(username) {
        //Ext.get("user_display_name").dom.innerHTML = username;
        Ext.getCmp("user_display_name").setText(username);
    }
});
