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
        align: "middle"
    },
    border: false,
    items: [
        Ext.create("Ext.Img",{
            src: NOC.settings.logo_url,
            width: NOC.settings.logo_width,
            height: NOC.settings.logo_height
        }),

        {
            xtype: "container",
            html: NOC.settings.installation_name,
            style: {
                fontSize: "18px"
            },
            border: false
        },

        {
            xtype: "container",
            flex: 1
        },

        Ext.create("Ext.Button", {
            id: "user_display_name",
            text: "Anonymous",
            scale: "small",
            iconCls: "icon_user",
            menu: [
                {
                    id: "header_menu_toggle",
                    text: "Collapse all panels",
                    iconCls: "icon_arrow_out"
                },
                {
                    id: "header_menu_profile",
                    text: "User profile ...",
                    disabled: true,
                    iconCls: "icon_user_edit"
                },
                {
                    id: "header_menu_logout",
                    text: "Logout",
                    iconCls: "icon_cross"
                }
            ]
        }),
        
        {
            id: "search",
            xtype: "textfield",
            emptyText: "Search...",
            inputType: "search",
            listeners: {
                specialkey: function(field, event) {
                    var k = event.getKey();
                    if(k == event.ENTER) {
                        this.fireEvent("search", this.getValue());
                    } else if(k == event.ESC) {
                        this.reset();
                    }
                }
            }
        }
    ],
    // Change displayed username
    set_user_name: function(username) {
        //Ext.get("user_display_name").dom.innerHTML = username;
        Ext.getCmp("user_display_name").setText(username);
    }
});
