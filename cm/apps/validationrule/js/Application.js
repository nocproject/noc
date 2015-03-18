//---------------------------------------------------------------------
// cm.validationrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationrule.Application");

Ext.define("NOC.cm.validationrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.cm.validationrule.Model",
        "NOC.main.ref.validator.LookupField",
        "NOC.sa.managedobject.LookupField",
        "NOC.sa.managedobjectselector.LookupField"
    ],
    model: "NOC.cm.validationrule.Model",
    search: true,
    V_ACTIONS: [
        ["", "Ignore"],
        ["I", "Include"],
        ["X", "Exclude"]
    ],
    V_CHOICES: {
        "": "Ignore",
        "I": "Include",
        "X": "Exclude"
    },
    initComponent: function() {
        var me = this;

        me.currentConfigForm = null;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: "Active",
                    dataIndex: "is_active",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: "Scope",
                    dataIndex: "scope",
                    width: 100
                },
                {
                    text: "Description",
                    dataIndex: "description",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: "Active"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description"
                },
                {
                    name: "handler",
                    xtype: "main.ref.validator.LookupField",
                    fieldLabel: "Handler",
                    allowBlank: false,
                    listeners: {
                        scope: me,
                        select: me.onSelectHandler
                    }
                },
                {
                    name: "selectors_list",
                    xtype: "gridfield",
                    fieldLabel: "Selectors",
                    columns: [
                        {
                            text: "Action",
                            dataIndex: "action",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: me.V_ACTIONS
                            },
                            renderer: NOC.render.Choices(me.V_CHOICES)
                        },
                        {
                            text: "Selector",
                            dataIndex: "selector",
                            flex: 1,
                            editor: "sa.managedobjectselector.LookupField",
                            renderer: NOC.render.Lookup("selector")
                        }
                    ]
                },
                {
                    name: "objects_list",
                    xtype: "gridfield",
                    fieldLabel: "Objects",
                    columns: [
                        {
                            text: "Action",
                            dataIndex: "action",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: me.V_ACTIONS
                            },
                            renderer: NOC.render.Choices(me.V_CHOICES)
                        },
                        {
                            text: "Object",
                            dataIndex: "object",
                            flex: 1,
                            editor: "sa.managedobject.LookupField",
                            renderer: NOC.render.Lookup("object")
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.handlerField = me.form.findField("handler");
        me.cfHash = null;
    },
    //
    onSelectHandler: function(combo, record, eOpts) {
        var me = this;
        me.setConfigForm(record);
    },
    //
    setConfigForm: function(record) {
        var me = this,
            cf,
            form = me.formPanel.items.first(),
            cfHash;
        //
        cf = record.get("form") || [];
        cfHash = Ext.encode(cf);
        if(cfHash !== me.cfHash) {
            // Remove old config form
            if(me.currentConfigForm) {
                me.formPanel.remove(me.currentConfigForm);
                me.currentConfigForm.destroy();
                me.currentConfigForm = null;
                me.cfHash = null;
            }
            // Create new config form
            if(cf.length > 0) {
                me.currentConfigForm = Ext.create("Ext.ux.form.FormField", {
                    name: "config",
                    fieldLabel: "Config",
                    anchor: "100%",
                    form: cf
                });
                me.cfHash = cfHash;
                // Insert form field before selectors
                form.insert(5, me.currentConfigForm);
            }
        }
        // Set values
        if(me.currentConfigForm !== null && me.currentRecord !== null) {
            me.currentConfigForm.setValue(
                me.currentRecord.get("config")
            );
        }
    },
    //
    editRecord: function(record) {
        var me = this;
        me.callParent([record]);
        // Set the record and fire select event
        me.handlerField.setValue(record.get("handler"), true);
    }
});
