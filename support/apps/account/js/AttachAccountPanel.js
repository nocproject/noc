//---------------------------------------------------------------------
//
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.support.account.AttachAccountPanel");

Ext.define("NOC.support.account.AttachAccountPanel", {
    extend: "Ext.Window",
    title: "Attach existing account",
    layout: "fit",
    autoShow: true,
    draggable: false,
    resizable: false,
    closable: false,
    modal: true,
    app: null,
    width: 400,
    
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
                    name: "name",
                    fieldLabel: "Login",
                    allowBlank: false
                },
                {
                    xtype: "textfield",
                    name: "password",
                    fieldLabel: "Password",
                    allowBlank: false,
                    inputType: "password"
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
                    text: "Attach account",
                    glyph: NOC.glyph.save,
                    disabled: true,
                    formBind: true,
                    scope: me,
                    handler: me.onAttachAccount
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
        //me.form.getForm().getFields().first().focus();
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
    onAttachAccount: function() {
        var me = this,
            form = me.form.getForm();
        if(form.isValid()) {
            me.attachAccount(form.getValues());
        }
    },
    //
    attachAccount: function(values) {
        var me = this;
        Ext.Ajax.request({
            method: "POST",
            url: "/support/account/account/attach/",
            params: values,
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                if(data.status) {
                    me.close();
                    me.app.getInfo();
                } else {
                    NOC.error(data.message);
                }
            },
            failure: function() {
                NOC.error("Failed to attach account");
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
                me.onAttachAccount();
                break;
            case Ext.EventObject.ESC:
                key.stopEvent();
                me.onReset();
                break;
        }
    }
});
