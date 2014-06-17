//---------------------------------------------------------------------
// Login window
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.ChangeCredentials");

Ext.define("NOC.main.desktop.ChangeCredentials", {
    extend: "Ext.Window",
    title: "Change password",
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
                    items: this.change_credentials_fields
                }
            ],
            buttonAlign: "center",
            buttons: [
                {
                    text: "Close",
                    itemId: "close",
                    glyph: NOC.glyph.times,
                    handler: function() {
                        this.up("window").close();
                    }
                },
                {
                    text: "Reset",
                    itemId: "reset",
                    glyph: NOC.glyph.undo,
                    handler: function() {
                        this.up("window").down("form").getForm().reset();
                    }
                },
        
                {
                    text: "Change",
                    itemId: "change",
                    glyph: NOC.glyph.save,
                    // disabled: true,
                    // formBind: true,  @todo: Fix
                    handler: function() {
                        // Validate form
                        var win = this.up("window");
                        var form = win.down("form").getForm();
                        if(!form.isValid())
                            return;
                        var v = form.getValues();
                        win.controller.do_change_credentials(v);
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
        this.callParent()
    }
});
