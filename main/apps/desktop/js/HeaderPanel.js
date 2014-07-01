//---------------------------------------------------------------------
// Header
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.HeaderPanel");
Ext.define("NOC.main.desktop.HeaderPanel", {
    extend: "Ext.Panel",
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
    app: null,
    //
    initComponent: function() {
        var me = this,
            padding = 4,
            magic = 4,
            textHeight = 22,
            headerHeight = padding + magic + Math.max(NOC.settings.logo_height, textHeight);
        // User menu
        me.userMenuButton = Ext.create("Ext.button.Button", {
            text: "Anonymous",
            scale: "small",
            glyph: NOC.glyph.user,
            hidden: true,
            menu: [
                {
                    text: "About NOC",
                    glyph: NOC.glyph.question_circle,
                    scope: me.app,
                    handler: me.app.onAbout
                },
                "-",
                {
                    text: "User profile ...",
                    glyph: NOC.glyph.cog,
                    scope: me.app,
                    handler: me.app.onUserProfile
                },
                {
                    itemId: "header_menu_change_password",
                    text: "Change password ...",
                    disabled: true, // Changed on login
                    glyph: NOC.glyph.lock,
                    scope: me.app,
                    handler: me.app.onChangeCredentials
                },
                "-",
                {
                    text: "Logout",
                    glyph: NOC.glyph.power_off,
                    scope: me.app,
                    handler: me.app.onLogout
                }
            ]
        });
        //
        Ext.apply(me, {
            bodyPadding: padding,
            height: headerHeight,
            maxHeight: headerHeight,
            minHeight: headerHeight,
            items: [
                // NOC logo
                Ext.create("Ext.Img",{
                    src: NOC.settings.logo_url,
                    style: {
                        width: NOC.settings.logo_width + "px",
                        height: NOC.settings.logo_height + "px"
                    }
                }),
                // Bold NOC|
                {
                    xtype: "container",
                    html: "&nbsp;NOC| ",
                    style: {
                        fontSize: "18px",
                        fontWeight: "bold"
                    },
                    border: false
                },
                // Installation name
                {
                    xtype: "container",
                    flex: 1,
                    html: NOC.settings.installation_name,
                    style: {
                        fontSize: "18px"
                    },
                    border: false
                },
                // User menu
                me.userMenuButton,
                // Search field
                {
                    xtype: "textfield",
                    padding: "0 0 0 4",
                    emptyText: "Search...",
                    //inputType: "search",
                    listeners: {
                        specialkey: function(field, event) {
                            var k = event.getKey();
                            if(k == event.ENTER) {
                                me.app.onSearch(field.getValue());
                            } else if(k == event.ESC) {
                                field.reset();
                            }
                        }
                    }
                }
            ]
        });
        me.userProfileItem = me.userMenuButton.menu.getComponent("header_menu_change_password");
        me.callParent();
    },
    // Change displayed username
    setUserName: function(username) {
        var me = this;
        me.userMenuButton.setText(username);
    },
    //
    hideUserMenu: function() {
        var me = this;
        me.userMenuButton.hide();
    },
    //
    showUserMenu: function(canChangeCredentials) {
        var me = this;
        me.userProfileItem.setDisabled(!canChangeCredentials);
        me.userMenuButton.show();
    }
});
