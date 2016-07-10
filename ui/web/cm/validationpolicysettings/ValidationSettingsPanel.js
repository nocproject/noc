//---------------------------------------------------------------------
// NOC.core.MetricSettingsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationpolicysettings.ValidationSettingsPanel");

Ext.define("NOC.cm.validationpolicysettings.ValidationSettingsPanel", {
    extend: "Ext.tab.Panel",
    requires: [
        "NOC.cm.validationpolicy.LookupField"
    ],
    layout: "fit",
    app: null,
    template: null,
    validationModelId: null,
    title: "Validation Settings",
    autoScroll: true,
    scope: 0,

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            fields: [
                "policy", "policy__label", "is_active"
            ]
        });

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
                            text: "Policy",
                            dataIndex: "policy",
                            flex: 1,
                            renderer: NOC.render.Lookup("policy"),
                            editor: "cm.validationpolicy.LookupField"
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
        Ext.apply(me, {
            items: [
                me.settingsPanel
            ]
        });
        me.callParent();
        me.policiesField = me.settingsPanel.items.items[0];
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
            url: "/cm/validationpolicysettings/" + me.validationModelId + "/" + me.currentRecord.get("id") + "/settings/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.policiesField.setValue(data);
            },
            failure: function(response) {
                NOC.error("Cannot get settings");
            }
        });
    },
    //
    onSaveSettings: function() {
        var me = this,
            pollProgress = function(url) {
                Ext.Ajax.request({
                    url: url,
                    method: "GET",
                    scope: me,
                    success: onSuccess,
                    failure: onFailure
                });
            },
            onSuccess = function(response) {
                if(response.status === 202) {
                    // Future in progress
                    Ext.Function.defer(
                        pollProgress, 1000, me,
                        [response.getResponseHeader("Location")]
                    );
                } else {
                    // Process result
                    me.unmask();
                    me.loadSettings();
                }
            },
            onFailure = function(response) {
                var data = response.responseText ? Ext.decode(response.responseText) : null;
                if(data && data.success === false) {
                    NOC.error(data.message);
                } else {
                    NOC.error("Error saving record!");
                    console.log(response.responseText);
                }
                me.unmask();
            };

        me.mask();
        Ext.Ajax.request({
            url: "/cm/validationpolicysettings/" + me.validationModelId + "/" + me.currentRecord.get("id") + "/settings/",
            method: "POST",
            jsonData: {
                policies: me.policiesField.getValue()
            },
            scope: me,
            success: onSuccess,
            failure: onFailure
        });
    }
});
