//---------------------------------------------------------------------
// main.userprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.userprofile.Application");

Ext.define("NOC.main.userprofile.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.main.timepattern.LookupField",
        "NOC.main.ref.unotificationmethod.LookupField",
        "NOC.main.ref.ulanguage.LookupField",
        "Ext.ux.form.GridField"
    ],
    layout: "fit",
    //
    initComponent: function() {
        var me = this;
        me.usernameField = Ext.create("Ext.form.field.Display", {
            fieldLabel: __("Login")
        });
        me.nameField = Ext.create("Ext.form.field.Display", {
            fieldLabel: __("Name")
        });
        me.emailField = Ext.create("Ext.form.field.Display", {
            fieldLabel: __("Mail")
        });
        me.languageField = Ext.create("NOC.main.ref.ulanguage.LookupField", {
            fieldLabel: __("Language"),
            allowBlank: false
        });
        me.groupsField = Ext.create("Ext.form.field.Display", {
            fieldLabel: __("Groups")
        });
        // Contacts grid
        me.contactsGrid = Ext.create({
            xtype: "gridfield",
            columns: [
                {
                    text: __("Time Pattern"),
                    dataIndex: "time_pattern",
                    width: 150,
                    renderer: NOC.render.Lookup("time_pattern"),
                    editor: "main.timepattern.LookupField"
                },
                {
                    text: __("Method"),
                    dataIndex: "notification_method",
                    width: 120,
                    editor: "main.ref.unotificationmethod.LookupField"
                },
                {
                    text: __("Params"),
                    dataIndex: "params",
                    flex: 1,
                    editor: "textfield"
                }
            ],
            getValue: function() {
                var grid = this, records = [];
                this.store.each(function(r) {
                    var d = {};
                    Ext.each(grid.fields, function(f) {
                        // ToDo change Ext.ux.form.GridField
                        var field_name = f.name || f;
                        d[field_name] = r.get(field_name);
                    });
                    records.push(d);
                });
                return records;
            }
        });
        Ext.apply(me, {
            items: [
                {
                    xtype: "form",
                    defaults: {
                        padding: "0 0 0 4px"
                    },
                    items: [
                        me.usernameField,
                        me.groupsField,
                        me.nameField,
                        me.emailField,
                        me.languageField,
                        {
                            xtype: "fieldset",
                            title: __("Notification Contacts"),
                            defaults: {
                                padding: 4
                            },
                            border: false,
                            items: [
                                me.contactsGrid
                            ]
                        }
                    ],
                    dockedItems: [
                        {
                            xtype: "toolbar",
                            dock: "top",
                            items: [
                                {
                                    glyph: NOC.glyph.save,
                                    text: __("Save"),
                                    scope: me,
                                    handler: me.onSave
                                }
                            ]
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.loadData();
        me.setHistoryHash();
    },
    //
    loadData: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/main/userprofile/",
            method: "GET",
            scope: me,
            success: function(response) {
                me.setData(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.msg.failed(__("Failed to load data"))
            }
        });
    },
    //
    setData: function(data) {
        var me = this;
        me.profileData = data;
        me.usernameField.setValue(data.username);
        me.nameField.setValue(data.name);
        me.emailField.setValue(data.email);
        me.languageField.setValue(data.preferred_language);
        me.groupsField.setRawValue((data.groups || []).join(", "));
        me.contactsGrid.setValue(data.contacts || []);
    },
    //
    onSave: function() {
        var me = this,
            data = {
                preferred_language: me.languageField.getValue(),
                contacts: me.contactsGrid.getValue()
            };
        Ext.Ajax.request({
            url: "/main/userprofile/",
            method: "POST",
            jsonData: data,
            success: function() {
                NOC.msg.complete(__("Profile saved"));
                if(me.profileData.preferred_language !== data.preferred_language) {
                    NOC.app.app.restartApplication(__("Changing language"));
                }
            },
            failure: function() {
                NOC.msg.failed(__("Failed to save"))
            }
        });
    }
});
