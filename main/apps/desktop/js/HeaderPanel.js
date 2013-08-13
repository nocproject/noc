//---------------------------------------------------------------------
// Header
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
(function(){
    console.debug("Defining NOC.main.desktop.HeaderPanel");

    var _padding = 4, _magic = 4, _text_height = 22;
    var _header_height = _padding + _magic;
    _header_height += NOC.settings.logo_height > _text_height ? NOC.settings.logo_height : _text_height;

    Ext.define("NOC.main.desktop.HeaderPanel", {
        extend: "Ext.Panel",
        id: "header",
        region: "north",
        layout: {
            type: "hbox",
            align: "middle"
        },
        border: false,
        // bodyCls: Ext.baseCSSPrefix + 'toolbar',
        bodyPadding: _padding,
        height: _header_height,
        maxHeight: _header_height,
        minHeight: _header_height,
        collapsible: true,
        animCollapse: true,
        collapseMode: "mini",
        split: true,
        preventHeader: true,
        items: [
            Ext.create("Ext.Img",{
                src: NOC.settings.logo_url,
                width: NOC.settings.logo_width,
                height: NOC.settings.logo_height
            }),
            {
                xtype: "container",
                html: "NOC:&nbsp;",
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
                iconCls: "icon_user",
                hidden: true,
                menu: [
                    {
                        id: "header_menu_toggle",
                        text: "Collapse all panels",
                        iconCls: "icon_arrow_out"
                    },
                    "-",
                    {
                        id: "header_menu_userprofile",
                        text: "User profile ...",
                        disabled: true,
                        iconCls: "icon_user_edit"
                    },
                    {
                        id: "header_menu_change_password",
                        itemId: Ext.getCmp("header"),
                        text: "Change password ...",
                        disabled: true,
                        iconCls: "icon_user_green"
                    },
                    "-",
                    {
                        id: "header_menu_logout",
                        text: "Logout",
                        iconCls: "icon_door_out"
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
        // Change displayed username
        set_user_name: function(username) {
            var b = Ext.getCmp("user_display_name");
            b.setText(username);
        }
    });
})();
