//---------------------------------------------------------------------
// NOC.core.MetricSettingsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.MetricSettingsPanel");

Ext.define("NOC.core.MetricSettingsPanel", {
    extend: "Ext.tab.Panel",
    layout: "fit",
    app: null,
    template: null,
    metricModelId: null,
    title: "Metric Settings",
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.effectiveSettingsStore = Ext.create("Ext.data.Store", {
            fields: [
                "metric",
                "metric_type",
                "is_active",
                "storage_rule",
                "probe",
                "interval",
                "thresholds",
                "handler",
                "config",
                "errors",
                "traces",
                "retentions"
            ]
        });
        // Settings panel
        me.settingsPanel = Ext.create("Ext.panel.Panel", {
            title: "Settings",
            layout: "fit",
            autoScroll: true,
            items: [
                {
                    xtype: "gridfield",
                    layout: "fit",
                    columns: [
                        {
                            text: "Active",
                            dataIndex: "is_active",
                            width: 50,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: "Metric Set",
                            dataIndex: "metric_set",
                            flex: 1,
                            renderer: NOC.render.Lookup("metric_set")
                        }
                    ]
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            xtype: "button",
                            text: "Close",
                            glyph: NOC.glyph.arrow_left,
                            scope: me,
                            handler: me.onClose
                        },
                        "-",
                        {
                            xtype: "button",
                            text: "Save",
                            glyph: NOC.glyph.save,
                            scope: me,
                            handler: me.onSaveSettings
                        }
                    ]
                }
            ]
        });
        //
        me.metricsPanel = Ext.create("Ext.panel.Panel", {
            layout: "fit",
            title: "Metrics",
            autoScroll: true,
            items: [
                {
                    xtype: "grid",
                    store: me.effectiveSettingsStore,
                    autoScroll: true,
                    stateful: true,
                    stateId: "noc-metricsettings-metrics",
                    columns: [
                        {
                            text: "Metric",
                            dataIndex: "metric",
                            width: 400
                        },
                        {
                            text: "Active",
                            dataIndex: "is_active",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: "Interval",
                            dataIndex: "interval",
                            width: 50,
                            align: "right"
                        },
                        {
                            text: "Metric Type",
                            dataIndex: "metric_type",
                            width: 200
                        },
                        {
                            text: "Thresholds",
                            dataIndex: "thresholds",
                            width: 100,
                            renderer: function(value) {
                                if(!value) {
                                    value = [null, null, null, null]
                                }
                                value = value.map(function(v) {
                                    if(v === null) {
                                        return "-"
                                    } else {
                                        return v;
                                    }
                                });
                                return value.join(" | ");
                            }
                        },
                        {
                            text: "Storage Rule",
                            dataIndex: "storage_rule",
                            width: 100
                        },
                        {
                            text: "Retentions",
                            dataIndex: "retentions",
                            width: 100
                        },
                        {
                            text: "Probe",
                            dataIndex: "probe",
                            width: 100
                        }
                    ]
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            xtype: "button",
                            text: "Close",
                            glyph: NOC.glyph.arrow_left,
                            scope: me,
                            handler: me.onClose
                        }
                    ]
                }
            ]
        });
        //
        me.detailsGrid = Ext.create("Ext.grid.Panel", {
            autoScroll: true,
            layout: "fit",
            stateful: true,
            stateId: "noc-metricsettings-metrics",
            store: me.effectiveSettingsStore,
            flex: 1,
            columns: [
                {
                    text: "Metric",
                    dataIndex: "metric",
                    width: 400
                },
                {
                    text: "Active",
                    dataIndex: "is_active",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: "Metric Type",
                    dataIndex: "metric_type",
                    width: 200
                }
            ],
            listeners: {
                scope: me,
                select: me.onDetailSelected
            }
        });

        me.configPanel = Ext.create("Ext.grid.property.Grid", {
            title: "Config",
            autoScroll: true,
            flex: 1,
            source: {}
        });

        me.tracePanel = Ext.create("Ext.container.Container", {
            title: "Trace",
            autoScroll: true,
            html: "",
            flex: 1,
            padding: 4
        });

        me.detailsPanel = Ext.create("Ext.panel.Panel", {
            title: "Details",
            layout: "fit",
            autoScroll: true,
            items: [{
                xtype: "container",
                layout: {
                    type: "hbox",
                    align: "stretch"
                },
                items: [
                    me.detailsGrid,
                    {
                        xtype: "container",
                        layout: {
                            type: "vbox",
                            align: "stretch"
                        },
                        flex: 1,
                        items: [
                            me.configPanel,
                            me.tracePanel
                        ]
                    }
                ]
            }],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            xtype: "button",
                            text: "Close",
                            glyph: NOC.glyph.arrow_left,
                            scope: me,
                            handler: me.onClose
                        }
                    ]
                }
            ]
        });
        //
        Ext.apply(me, {
            items: [
                me.settingsPanel,
                me.metricsPanel,
                me.detailsPanel
            ]
        });
        me.callParent();
        me.metricSetsField = me.settingsPanel.items.items[0];
    },

    //
    preview: function(record) {
        var me = this;
        me.currentRecord = record;
        me.loadSettings();
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    },
    //
    loadSettings: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/pm/metricsettings/" + me.metricModelId + "/" + me.currentRecord.get("id") + "/settings/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.metricSetsField.setValue(data);
            },
            failure: function(response) {
                NOC.error("Cannot get settings");
            }
        });
        Ext.Ajax.request({
            url: "/pm/metricsettings/" + me.metricModelId + "/" + me.currentRecord.get("id") + "/effective/trace/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.effectiveSettingsStore.loadData(data);
            },
            failure: function(response) {
                NOC.error("Cannot get settings");
            }
        });
    },
    //
    onSaveSettings: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/pm/metricsettings/" + me.metricModelId + "/" + me.currentRecord.get("id") + "/settings/",
            method: "POST",
            jsonData: {
                metric_sets: me.metricSetsField.getValue()
            },
            scope: me,
            success: function() {
                NOC.info("Saved");
                me.loadSettings();
            },
            failure: function() {
                NOC.error("Failed to save");
            }
        });
    },
    //
    onDetailSelected: function(panel, record) {
        var me = this,
            r = [], i,
            errors = record.get("errors") || [],
            traces = record.get("traces") || [],
            handler = record.get("handler") || "No handler";
        console.log(record.data);
        me.configPanel.setSource(record.get("config"));
        me.configPanel.setTitle("Handler: " + handler);
        if(errors.length) {
            r.push("<b>ERRORS:</b>");
            for(i = 0; i < errors.length; i++) {
                r.push(errors[i]);
            }
        }
        if(traces.length) {
            r.push("<b>TRACE:</b>");
            for(i = 0; i < traces.length; i++) {
                r.push(traces[i]);
            }
        }
        me.tracePanel.update("<pre>" + r.join("\n") + "</pre>");
    }
});
