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

    initComponent: function() {
        console.log(this.fields);
        Ext.applyIf(this, {
            items: [
                {
                    xtype: "form",
                    bodyPadding: 4,
                    border: false,
                    defaults: {
                        enableKeyEvents: true,
                        listeners: {
                            scope: this,
                            specialkey: function(field, key) {
                                if (field.xtype != "textfield")
                                    return;
                                var get_button = function(scope, name) {
                                    return scope.down("panel").dockedItems.items[0].getComponent(name);
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
                    items: this.login_fields,
                    buttonAlign: "center",
                    buttons: [
                        {
                            text: "Reset",
                            itemId: "reset",
                            glyph: NOC.glyph.undo,
                            handler: function() {
                                this.up("form").getForm().reset();
                            }
                        },

                        {
                            text: "Login",
                            itemId: "login",
                            glyph: NOC.glyph.check,
                            disabled: true,
                            formBind: true,
                            handler: function() {
                                // Validate form
                                var win = this.up("window");
                                var form = this.up("form").getForm();
                                if(!form.isValid())
                                    return;
                                var v = form.getValues();
                                win.controller.do_login(v);
                            }
                        }
                    ],
                    listeners: {
                        afterrender: function() {
                            this.getForm().getFields().first().focus(false, 100);
                            return true;
                        }
                    }
                }
            ]
        });
        this.callParent()
    }
});
