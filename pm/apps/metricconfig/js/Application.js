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
        "NOC.pm.storagerule.LookupField",
        "NOC.pm.probe.LookupField",
        "NOC.pm.metrictype.LookupField",
        "NOC.main.ref.probehandler.LookupField"
    ],
    model: "NOC.pm.metricconfig.Model",
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
                    allowBlank: false
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
                    allowBlank: true
                },
                {
                    name: "handler",
                    xtype: "main.ref.probehandler.LookupField",
                    fieldLabel: "Handler",
                    allowBlank: false,
                    listeners: {
                        scope: me,
                        change: me.onChangeHandler
                    }
                },
                {
                    name: "probe",
                    xtype: "pm.probe.LookupField",
                    fieldLabel: "Probe",
                    allowBlank: false
                },
                {
                    name: "storage_rule",
                    xtype: "pm.storagerule.LookupField",
                    fieldLabel: "Storage Rule",
                    allowBlank: false
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
    },
    //
    onChangeHandler: function(combo, newValue, oldValue, eOpts) {
        var me = this,
            metrics,
            r = [],
            form = me.formPanel.items.first(),
            currentConfig = {},
            vm, cf, f;
        if((newValue === oldValue)) {
            return;
        }
        if(!oldValue && newValue) {
            vm = combo.valueModels[0];
            if(me.form.getValues().metrics.length === 0) {
                // Fill available metrics
                r = vm.get("metrics").map(function (v) {
                    return {
                        metric_type: v.id,
                        metric_type__label: v.label,
                        is_active: true
                    }
                });
                me.form.setValues({
                    metrics: r
                });
            }
            cf = vm.get("form");
            if(!me.currentConfigForm || (me.currentConfigForm.xtype != cf)) {
                if(me.currentConfigForm) {
                    // Delete old config
                    currentConfig = me.currentConfigForm.getValue();
                    me.formPanel.remove(me.currentConfigForm);
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
        }
    }
});
