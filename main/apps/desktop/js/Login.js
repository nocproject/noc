//---------------------------------------------------------------------
// Login window
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.Login");

Ext.define("NOC.main.desktop.Login", {
    extend: "Ext.window.Window",
    title: "NOC Login: " + NOC.settings.installation_name,
    layout: "fit",
    autoShow: true,
    draggable: false,
    resizable: false,
    closable: false,
    modal: true,
    app: null,
    fields: [],
    width: 300,
    autoScroll: true,

    initComponent: function() {
        var me = this;

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
            items: me.fields,
            buttonAlign: "center",
            buttons: [
                {
                    text: "Reset",
                    glyph: NOC.glyph.undo,
                    scope: me,
                    handler: me.onReset
                },

                {
                    text: "Login",
                    glyph: NOC.glyph.sign_in,
                    disabled: true,
                    formBind: true,
                    scope: me,
                    handler: me.onLogin
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
        me.form.getForm().getFields().first().focus();
    },
    // Reset button pressed
    onReset: function() {
        var me = this;
        me.form.getForm().reset();
    },
    // Login button pressed
    onLogin: function() {
        var me = this,
            form = me.form.getForm();
        if(form.isValid()) {
            me.app.login(form.getValues());
        }
    },
    // Process special fields
    onSpecialKey: function(field, key) {
        var me = this;
        if (field.xtype != "textfield")
            return;
        switch(key.getKey()) {
            case Ext.EventObject.ENTER:
                key.stopEvent();
                me.onLogin();
                break;
            case Ext.EventObject.ESC:
                key.stopEvent();
                me.onReset();
                break;
        }
    }
});
