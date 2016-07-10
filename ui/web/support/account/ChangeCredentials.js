//---------------------------------------------------------------------
// Login window
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.support.account.ChangeCredentials");

Ext.define("NOC.support.account.ChangeCredentials", {
    extend: "Ext.Window",
    title: "Change Password",
    layout: "fit",
    autoShow: true,
    draggable: false,
    resizable: false,
    closable: false,
    modal: true,
    app: null,
    width: 400,
    minPasswordLength: 8,

    
    initComponent: function() {
        var me = this;
        //
        me.form = Ext.create("Ext.form.Panel", {
            bodyPadding: 4,
            border: false,
            defaults: {
                enableKeyEvents: true,
                anchor: "100%",
                listeners: {
                    scope: me,
                    specialkey: me.onSpecialKey
                }
            },
            items: [
                {
                    xtype: "textfield",
                    name: "old_password",
                    fieldLabel: "Old Password",
                    allowBlank: false,
                    inputType: "password"
                },
                {
                    xtype: "textfield",
                    name: "new_password",
                    fieldLabel: "New Password",
                    allowBlank: false,
                    inputType: "password",
                    minLength: me.minPasswordLength
                },
                {
                    xtype: "textfield",
                    name: "new_password2",
                    fieldLabel: "New Password (Retype)",
                    allowBlank: false,
                    inputType: "password",
                    vtype: "password",
                    peerField: "new_password",
                    minLength: me.minPasswordLength
                }
            ],
            buttonAlign: "center",
            buttons: [
                {
                    text: "Close",
                    glyph: NOC.glyph.times,
                    scope: me,
                    handler: me.onClose
                },
                {
                    text: "Reset",
                    glyph: NOC.glyph.undo,
                    scope: me,
                    handler: me.onReset
                },
                {
                    text: "Change",
                    glyph: NOC.glyph.save,
                    disabled: true,
                    formBind: true,
                    scope: me,
                    handler: me.onChangeCredentials
                }
            ]
        });

        Ext.apply(me, {
            items: [me.form]
        });
        me.callParent()
    },
    //
    afterRender: function() {
        var me = this;
        me.callParent();
        // Focus on first field
        me.form.getForm().getFields().first().focus();
    },
    // Close button pressed. Close window
    onClose: function() {
        var me = this;
        me.close();
    },
    // Reset button pressed. Clear form
    onReset: function() {
        var me = this;
        me.form.getForm().reset();
    },
    // Change credentials form pressed
    onChangeCredentials: function() {
        var me = this,
            form = me.form.getForm();
        if(form.isValid()) {
            me.changeCredentials(form.getValues());
        } else {
            NOC.error("Invalid credentials");
        }
    },
    //
    changeCredentials: function(values) {
        var me = this;
        Ext.Ajax.request({
            method: "POST",
            url: "/support/account/account/change_password/",
            params: values,
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                if(data.status) {
                    NOC.info("Credentials has been changed");
                    me.close();
                } else {
                    NOC.error(data.message);
                }
            },
            failure: function(response) {
                var status = Ext.decode(response.responseText);
                NOC.error("Failed to change credentials: " + status.error);
            }
        });
    },
    //
    onSpecialKey: function(field, key) {
        var me = this;
        if (field.xtype !== "textfield")
            return;
        switch(key.getKey()) {
            case Ext.EventObject.ENTER:
                key.stopEvent();
                me.onChangeCredentials();
                break;
            case Ext.EventObject.ESC:
                key.stopEvent();
                me.onReset();
                break;
        }
    }
});
