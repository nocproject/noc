//---------------------------------------------------------------------
// Login window
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
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
            handler: function() {
                this.up("window").down("form").getForm().reset();
            }
        },

        {
            text: "Login",
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
    ]
});
