//---------------------------------------------------------------------
// support.account AccountPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.support.account.AccountPanel");

Ext.define("NOC.support.account.AccountPanel", {
    extend: "Ext.panel.Panel",
    requires: [
        "NOC.main.ref.country.LookupField"
    ],
    app: null,
    title: "Account",
    layout: "fit",
    autoScroll: true,
    closable: false,

    minPasswordLength: 8,
    notRegisteredText: "Account is not registred. Please register account to get access to additional support and services",
    registeredText: "Account is registred. You have access to additional support and serivces",
    industries: [
        ["ISP", "Internet Service Provider"],
        ["DC", "Hosting & Datacenter Service Provider"],
        ["ASP", "Application Service Provider"],
        ["PSP", "Payment Service Provider"],
        ["SI", "System Intergration"],
        ["SD", "Software Development"],
        ["EDU", "Educational"],
        ["SCI", "Science&Research"],
        ["GOV", "Government"]
    ],

    initComponent: function() {
        var me = this;

        me.attachButton = Ext.create("Ext.button.Button", {
            text: "Attach existing account",
            glyph: NOC.glyph.plus_circle,
            scope: me,
            handler: me.onAttachAccount
        });

        me.changePasswordButton = Ext.create("Ext.button.Button", {
            text: "Change password",
            glyph: NOC.glyph.lock,
            scope: me,
            handler: me.onChangePassword
        });

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
                    fieldLabel: "Login",
                    allowBlank: false,
                    regex: /^[a-z0-9\.\-_]+$/i
                },
                {
                    xtype: "textfield",
                    name: "org",
                    fieldLabel: "Company",
                    allowBlank: true
                },
                {
                    xtype: "textfield",
                    name: "email",
                    fieldLabel: "Mail",
                    allowBlank: false,
                    vtype: "email"
                },
                {
                    xtype: "main.ref.country.LookupField",
                    name: "country",
                    fieldLabel: "Country"
                },
                {
                    xtype: "combobox",
                    name: "language",
                    fieldLabel: "Preferred Language",
                    allowBlank: false,
                    store: [
                        ["EN", "English"],
                        ["RU", "Русский"]
                    ],
                    value: "EN"
                },
                {
                    xtype: "fieldset",
                    title: "Industries",
                    layout: {
                        type: "table",
                        columns: 2
                    },
                    items: me.getIndustriesFields()
                },
                {
                    xtype: "textfield",
                    name: "password",
                    fieldLabel: "Password",
                    itemId: "password",
                    inputType: "password",
                    allowBlank: false,
                    minLength: me.minPasswordLength
                },
                {
                    xtype: "textfield",
                    name: "password2",
                    fieldLabel: "Retype password",
                    itemId: "password2",
                    inputType: "password",
                    vtype: "password",
                    peerField: "password",
                    allowBlank: false,
                    minLength: me.minPasswordLength
                }
            ],
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.saveButton,
                    me.attachButton,
                    me.changePasswordButton
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
        me.attachButton.show();
        me.changePasswordButton.hide();
        me.infoText.setHtml(me.notRegisteredText);
        me.infoText.addCls("noc-alert-warning");
        me.infoText.removeCls("noc-alert-success");
        me.form.getComponent("password").show();
        me.form.getComponent("password").setDisabled(false);
        me.form.getComponent("password2").show();
        me.form.getComponent("password2").setDisabled(false);
        me.form.getComponent("uuid").hide();
    },
    //
    setRegistered: function(data) {
        var me = this;
        me.attachButton.hide();
        me.changePasswordButton.show();
        me.infoText.setHtml(me.registeredText);
        me.infoText.addCls("noc-alert-success");
        me.infoText.removeCls("noc-alert-warning");
        me.form.getComponent("password").hide();
        me.form.getComponent("password").setDisabled(true);
        me.form.getComponent("password2").hide();
        me.form.getComponent("password2").setDisabled(true);
        me.form.getComponent("uuid").show();
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
        delete values["password2"];
        Ext.Ajax.request({
            url: "/support/account/account/",
            method: "POST",
            jsonData: values,
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                if(data.status) {
                    NOC.info("Account saved");
                    me.app.getInfo();
                } else {
                    NOC.error(data.message);
                }
            },
            failure: function() {
                NOC.error("Failed to save account");
            }
        });
    },
    //
    onAttachAccount: function() {
        var me = this;
        Ext.create("NOC.support.account.AttachAccountPanel", {app: me.app}).show();
    },
    //
    onChangePassword: function() {
        var me = this;
        Ext.create("NOC.support.account.ChangeCredentials", {app: me.app}).show();
    },
    //
    getIndustriesFields: function() {
        var me = this;
        return me.industries.map(function(v) {
            return {
                xtype: "checkbox",
                name: "ind_" + v[0],
                boxLabel: v[1],
                inputValue: true
            }
        });
    }
});
