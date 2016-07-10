//---------------------------------------------------------------------
// support.account SystemPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.support.account.SystemPanel");

Ext.define("NOC.support.account.SystemPanel", {
    extend: "Ext.panel.Panel",
    app: null,
    title: "System",
    layout: "fit",
    autoScroll: true,
    closable: false,

    minPasswordLength: 8,
    notRegisteredText: "System is not registred. Please register your system to get access to additional support and services",
    registeredText: "System is registred. You have access to additional support and services",

    initComponent: function() {
        var me = this;

        me.saveButton = Ext.create("Ext.button.Button", {
            text: "Save",
            glyph: NOC.glyph.save,
            scope: me,
            handler: me.onSave,
            formBind: true,
            disabled: true
        });

        me.infoText = Ext.create("Ext.container.Container", {
            border: 2,
            html: self.notRegisteredText,
            cls: "noc-alert noc-alert-success"
        });

        me.form = Ext.create("Ext.form.Panel", {
            padding: 4,
            border: 0,
            items: [
                me.infoText,
                {
                    xtype: "displayfield",
                    name: "uuid",
                    fieldLabel: "UUID",
                    itemId: "uuid"
                },
                {
                    xtype: "textfield",
                    name: "name",
                    fieldLabel: "Name",
                    allowBlank: false,
                    regex: /^[a-z0-9\.\-_]+$/i
                },
                {
                    xtype: "combobox",
                    name: "type",
                    fieldLabel: "Type",
                    allowBlank: false,
                    store: [
                        ["dev", "Development"],
                        ["test", "Test"],
                        ["prod", "Productive"],
                        ["eval", "Evaluation"]
                    ],
                    value: "eval"
                },
                {
                    xtype: "textarea",
                    name: "description",
                    fieldLabel: "Description",
                    allowBlank: true,
                    anchor: "100%"
                }
            ],
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.saveButton
                ]
            }]
        });

        Ext.apply(me, {
            items: [
                me.form
            ]
        });
        me.callParent();
    },
    //
    setNotRegistered: function() {
        var me = this;
        me.infoText.setHtml(me.notRegisteredText);
        me.infoText.addCls("noc-alert-warning");
        me.infoText.removeCls("noc-alert-success");

    },
    //
    setRegistered: function(data) {
        var me = this;
        me.infoText.setHtml(me.registeredText);
        me.infoText.addCls("noc-alert-success");
        me.infoText.removeCls("noc-alert-warning");
        me.form.getForm().setValues(data);
    },
    //
    onSave: function() {
        var me = this,
            values;
        if(!me.form.isValid()) {
            NOC.error("Error in data");
            return;
        }
        values = me.form.getValues();
        Ext.Ajax.request({
            url: "/support/account/system/",
            method: "POST",
            jsonData: values,
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                if(data.status) {
                    NOC.info("System saved");
                    me.app.getInfo();
                } else {
                    NOC.error(data.message);
                }
            },
            failure: function() {
                NOC.error("Failed to save system");
            }
        });
    }
});
