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
    layout: {
        type: "hbox",
        align: "middle"
    },
    border: false,
    bodyStyle: {
        "background-color": NOC.settings.branding_background_color,
        "color": NOC.settings.branding_color
    },
    collapsible: true,
    animCollapse: true,
    collapseMode: "mini",
    //split: true,
    header: false,
    items: [
        Ext.create("Ext.Img",{
            src: NOC.settings.logo_url,
            width: NOC.settings.logo_width,
            height: NOC.settings.logo_height
        }),
        {
            xtype: "container",
            html: "&nbsp;NOC| ",
            style: {
                fontSize: "18px",
                fontWeight: "bold"
            },
            border: false
        },

        {
            xtype: "container",
            flex: 1,
            html: NOC.settings.installation_name,
            style: {
                fontSize: "18px"
            },
            border: false
        },

        {
            id: "user_display_name",
            xtype: "button",
            itemId: "user_display_name",
            text: "Anonymous",
            scale: "small",
            // iconCls: "icon_user",
            glyph: NOC.glyph.user,
            hidden: true,
            menu: [
                {
                    id: "header_menu_about",
                    text: "About NOC",
                    glyph: NOC.glyph.question_circle
                },
                {
                    id: "header_menu_toggle",
                    text: "Collapse all panels",
                    glyph: NOC.glyph.expand
                },
                "-",
                {
                    id: "header_menu_userprofile",
                    text: "User profile ...",
                    disabled: true,
                    glyph: NOC.glyph.cog
                },
                {
                    id: "header_menu_change_password",
                    itemId: Ext.getCmp("header"),
                    text: "Change password ...",
                    disabled: true,
                    glyph: NOC.glyph.lock
                },
                "-",
                {
                    id: "header_menu_logout",
                    text: "Logout",
                    glyph: NOC.glyph.power_off
                }
            ]
        },

        {
            id: "search",
            xtype: "textfield",
            padding: "0 0 0 4",
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
    //
    initComponent: function() {
        var me = this,
            padding = 4,
            magic = 4,
            textHeight = 22,
            headerHeight = padding + magic + Math.max(NOC.settings.logo_height, textHeight);
        Ext.apply(me, {
            bodyPadding: padding,
            height: headerHeight,
            maxHeight: headerHeight,
            minHeight: headerHeight
        });
        me.callParent();
    },
    // Change displayed username
    set_user_name: function(username) {
        var b = Ext.getCmp("user_display_name");
        b.setText(username);
    }
});
