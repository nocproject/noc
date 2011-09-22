//---------------------------------------------------------------------
// Login window
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.Login");

Ext.define("NOC.main.desktop.Login", {
    extend: "Ext.Window",
    title: "NOC Login: " + NOC.settings.installation_name,
    layout: "fit",
    autoShow: true,
    draggable: false,
    resizable: false,
    closable: false,
    modal: true,
    
    items: [
        {
            xtype: "form",
            bodyPadding: 4,
            border: false,
            defaults: {
                enableKeyEvents: true,
                listeners: {
                    specialkey: function(field, key) {
                        if (field.xtype != "textfield")
                            return;
                        var get_button = function(scope, name) {
                            return scope.up("panel").up("panel").dockedItems.items[1].getComponent(name);
                        }
                        switch(key.getKey()) {
                            case Ext.EventObject.ENTER:
                                var b = get_button(this, "login");
                                key.stopEvent();
                                b.handler.call(b);
                                break;
                            case Ext.EventObject.ESC:
                                var b = get_button(this, "reset");
                                key.stopEvent();
                                b.handler.call(b);
                        }
                    }
                }
            },
            items: [
                {
                    xtype: "textfield",
                    name: "username",
                    fieldLabel: "Name",
                    allowBlank: false,
                    emptyText: "Enter username"
                },

                {
                    xtype: "textfield",
                    name: "password",
                    fieldLabel: "Password",
                    allowBlank: false,
                    inputType: "password"
                }
            ]
        }
    ],
    buttons: [
        {
            text: "Reset",
            itemId: "reset",
            handler: function() {
                this.up("window").down("form").getForm().reset();
            }
        },

        {
            text: "Login",
            itemId: "login",
            // disabled: true,
            // formBind: true,  @todo: Fix
            handler: function() {
                // Validate form
                var win = this.up("window");
                var form = win.down("form").getForm();
                if(!form.isValid())
                    return;
                var v = form.getValues();
                win.controller.do_login(v);
            }
        }
    ],
    listeners: {
        afterrender: function() {
            this.down("form").getForm().getFields().first().focus(false, 100);
            return true;
        }
    }
});
