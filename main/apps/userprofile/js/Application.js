//---------------------------------------------------------------------
// main.userprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.userprofile.Application");

Ext.define("NOC.main.userprofile.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.main.timepattern.LookupField",
        "NOC.main.ref.unotificationmethod.LookupField"
    ],
    layout: "fit",
    //
    initComponent: function() {
        var me = this,
            lw = 60;
        me.currentTheme = null;

        me.usernameField = Ext.create("Ext.form.field.Display", {
            fieldLabel: "Login",
            labelWidth: lw
        });
        me.nameField = Ext.create("Ext.form.field.Display", {
            fieldLabel: "Name",
            labelWidth: lw
        });
        me.emailField = Ext.create("Ext.form.field.Display", {
            fieldLabel: "Mail",
            labelWidth: lw
        });
        me.languageField = Ext.create("NOC.main.ref.ulanguage.LookupField", {
            fieldLabel: "Language",
            labelWidth: lw
        });
        me.themeField = Ext.create("NOC.main.ref.theme.LookupField", {
            fieldLabel: "Theme",
            labelWidth: lw
        });
        // Contacts grid
        me.contactsStore = Ext.create("Ext.data.Store", {
            fields: [
                "time_pattern",
                "time_pattern__label",
                "notification_method",
                "params"
            ],
            data: []
        });
        me.contactsGrid = Ext.create("Ext.grid.Panel", {
            store: me.contactsStore,
            columns: [
                {
                    text: "Time Pattern",
                    dataIndex: "time_pattern",
                    width: 100,
                    renderer: NOC.render.Lookup("time_pattern"),
                    editor: "main.timepattern.LookupField"
                },
                {
                    text: "Method",
                    dataIndex: "notification_method",
                    width: 100,
                    editor: "main.ref.unotificationmethod.LookupField"
                },
                {
                    text: "Params",
                    dataIndex: "params",
                    flex: 1,
                    editor: "textfield"
                }
            ],
            plugins: [
                Ext.create("Ext.grid.plugin.RowEditing", {
                    clicksToEdit: 2
                })
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: "Add",
                            glyph: NOC.glyph.plus,
                            handler: function() {
                                var grid = this.up("panel"),
                                    rowEditing = grid.plugins[0];
                                rowEditing.cancelEdit();
                                grid.store.insert(0, {});
                                rowEditing.startEdit(0, 0);
                            }
                        },
                        {
                            text: "Delete",
                            glyph: NOC.glyph.times,
                            handler: function() {
                                var grid = this.up("panel"),
                                    sm = grid.getSelectionModel(),
                                    rowEditing = grid.plugins[0],
                                    app = grid.up("panel").up("panel");
                                rowEditing.cancelEdit();
                                grid.store.remove(sm.getSelection());
                                if(grid.store.getCount() > 0) {
                                    sm.select(0);
                                }
                                app.onInlineEdit();
                            }
                        }
                    ]
                }
            ],
            listeners: {
                validateedit: function(editor, e) {
                    // @todo: Bring to plugin
                    var form = editor.editor.getForm();
                    // Process comboboxes
                    form.getFields().each(function(field) {
                        e.record.set(field.name, field.getValue());
                        if(Ext.isDefined(field.getLookupData))
                            e.record.set(field.name + "__label",
                                         field.getLookupData());
                        });
                }
            }
        });
        //
        Ext.apply(me, {
            items: [
                {
                    xtype: "panel",
                    bodyPadding: 4,
                    items: [
                        me.usernameField,
                        me.nameField,
                        me.emailField,
                        me.languageField,
                        me.themeField,
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
                            text: "Save",
                            scope: me,
                            handler: me.onSave
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
                NOC.error("Failed to load data")
            }
        });
    },
    //
    setData: function(data) {
        var me = this;
        me.usernameField.setValue(data.username);
        me.nameField.setValue(data.name);
        me.emailField.setValue(data.email);
        me.languageField.setValue(data.preferred_language);
        me.themeField.setValue(data.theme);
        me.contactsStore.loadData(data.contacts);
        me.currentTheme = data.theme;
    },
    //
    onSave: function() {
        var me = this,
            data = {
                preferred_language: me.languageField.getValue(),
                theme: me.themeField.getValue(),
                contacts: me.contactsStore.data.items.map(function(x) {
                    return x.data
                })
            };
        Ext.Ajax.request({
            url: "/main/userprofile/",
            method: "POST",
            jsonData: data,
            success: function(response) {
                NOC.info("Profile saved");
                if(data.theme !== me.currentTheme) {
                    NOC.app.app.restartApplication("Applying theme changes");
                }
            },
            failure: function() {
                NOC.error("Failed to save")
            }
        });
    }
});
