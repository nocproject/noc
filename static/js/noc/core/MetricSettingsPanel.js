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
                        },
                    ]
                }
            ]
        });
        //
        Ext.apply(me, {
            items: [
                me.settingsPanel
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
                console.log(data);
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
                console.log(data);
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
    }
});
