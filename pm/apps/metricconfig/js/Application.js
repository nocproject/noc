//---------------------------------------------------------------------
// pm.metricconfig application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricconfig.Application");

Ext.define("NOC.pm.metricconfig.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.metricconfig.Model",
        "NOC.main.pool.LookupField",
        "NOC.pm.metrictype.LookupField",
        "NOC.main.ref.probehandler.LookupField"
    ],
    model: "NOC.pm.metricconfig.Model",
    search: true,
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
                    text: "Pool",
                    dataIndex: "pool",
                    width: 100,
                    renderer: NOC.render.Lookup("pool")
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
                    fieldLabel: "Description",
                    allowBlank: true,
                    uiStyle: "extra"
                },
                {
                    name: "pool",
                    xtype: "main.pool.LookupField",
                    fieldLabel: "Pool",
                    allowBlank: false
                },
                {
                    name: "handler",
                    xtype: "main.ref.probehandler.LookupField",
                    fieldLabel: "Handler",
                    allowBlank: false,
                    listeners: {
                        scope: me,
                        select: me.onSelectHandler
                    }
                },
                {
                    name: "interval",
                    xtype: "numberfield",
                    fieldLabel: "Interval",
                    allowBlank: false,
                    uiStyle: "small",
                    hideTrigger: true
                },
                {
                    name: "metrics",
                    xtype: "gridfield",
                    fieldLabel: "Metrics",
                    columns: [
                        {
                            text: "Type",
                            dataIndex: "metric_type",
                            width: 150,
                            renderer: NOC.render.Lookup("metric_type"),
                            editor: "pm.metrictype.LookupField"
                        },
                        {
                            text: "Active",
                            dataIndex: "is_active",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: "Meric",
                            dataIndex: "metric",
                            width: 250,
                            editor: {
                                xtype: "textfield",
                                regex: /^[0-9a-z_\-]+(\.[0-9a-z_\-]+)+$/i
                            }
                        },
                        {
                            text: "Low. Error",
                            dataIndex: "low_error",
                            width: 100,
                            align: "right",
                            editor: "numberfield"
                        },
                        {
                            text: "Low. Warn",
                            dataIndex: "low_warn",
                            width: 100,
                            align: "right",
                            editor: "numberfield"
                        },
                        {
                            text: "High. Warn",
                            dataIndex: "high_warn",
                            width: 100,
                            align: "right",
                            editor: "numberfield"
                        },
                        {
                            text: "High. Error",
                            dataIndex: "high_error",
                            width: 100,
                            align: "right",
                            editor: "numberfield"
                        }
                    ]
                }
            ]
        });
        me.callParent();
        me.handlerField = me.form.findField("handler");
    },
    //
    onSelectHandler: function(combo, record, eOpts) {
        var me = this;
        me.setConfigForm(record);
    },
    //
    setConfigForm: function(record) {
        var me = this,
            cf, f, cfHash,
            form = me.formPanel.items.first(),
            currentConfig = {},
            r = [];
        // Fill available metrics
        r = record.get("metrics").map(function (v) {
            return {
                metric_type: v.id,
                metric_type__label: v.label,
                is_active: true
            }
        });
        //
        me.form.setValues({
            metrics: r
        });
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
                form.insert(form.items.length - 2, me.currentConfigForm);
            }
        }
        // Set values
        if(me.currentConfigForm !== null && me.currentRecord !== null) {
            me.currentConfigForm.reset(true);
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
