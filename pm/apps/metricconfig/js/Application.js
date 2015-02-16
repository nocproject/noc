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
        "NOC.pm.probe.LookupField",
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
                    name: "probe",
                    xtype: "pm.probe.LookupField",
                    fieldLabel: "Probe",
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
            cf, f,
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
        me.form.setValues({
            metrics: r
        });
        //
        cf = record.get("form");
        if(!me.currentConfigForm || (me.currentConfigForm.xtype != cf)) {
            if(me.currentConfigForm) {
                // Delete old config
                currentConfig = me.currentConfigForm.getValue();
                me.formPanel.remove(me.currentConfigForm);
                me.currentConfigForm.destroy();
            } else {
                if(me.currentRecord) {
                    currentConfig = me.currentRecord.get("config");
                }
            }
            f = Ext.create(cf, {
                name: "config",
                fieldLabel: "Config"
            });
            // Insert before metrics grid
            form.insert(form.items.length - 2, f);
            f.setValue(currentConfig);
            me.currentConfigForm = f;
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
