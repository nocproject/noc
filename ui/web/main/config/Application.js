//---------------------------------------------------------------------
// main.config application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.config.Application");

Ext.define("NOC.main.config.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.main.config.ConfigModel"
    ],

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.main.config.ConfigModel",
            groupField: "section",
            autoLoad: false
        });

        me.configListStore = Ext.create("Ext.data.Store", {
            model: null,
            fields: ["id", "name"],
            data: [],
            autoLoad: false
        });

        me.searchField = Ext.create({
            xtype: "searchfield",
            name: "search",
            disabled: true,
            scope: me,
            handler: me.onSearch
        });

        me.saveButton = Ext.create("Ext.button.Button", {
            name: "save",
            text: __("Save"),
            glyph: NOC.glyph.save,
            disabled: true,
            scope: me,
            handler: me.onSave
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            border: false,
            autoScroll: true,
            stateful: true,
            stateId: "main.config-grid",
            bufferedRenderer: false, // Conflicts with grouping+cellediting
            store: me.store,
            features: [{
                ftype: "grouping",
                groupHeaderTpl: "[{name}]"
            }],
            selType: "rowmodel",
            plugins: [{
                ptype: "cellediting",
                clicksToEdit: 1
            }],
            columns: [
                {
                    text: __("Section"),
                    dataIndex: "section",
                    hidden: true
                },
                {
                    text: __("Key"),
                    dataIndex: "key",
                    width: 300
                },
                {
                    text: __("Default"),
                    dataIndex: "default",
                    flex: 1
                },
                {
                    text: __("Value"),
                    dataIndex: "value",
                    editor: "textfield",
                    flex: 1
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        "Config:",
                        {
                            xtype: "combobox",
                            name: "config",
                            itemId: "config",
                            width: 150,
                            emptytext: __("Select Config ..."),
                            store: me.configListStore,
                            queryMode: "local",
                            displayField: "name",
                            valueField: "id",
                            listeners: {
                                scope: me,
                                change: me.onConfigSelect
                            }
                        },
                        me.searchField,
                        "-",
                        me.saveButton
                    ]
                }
            ]
        });
        Ext.apply(me, {
            items: [me.grid]
        });
        me.callParent();
        me.current = null;
        // Load config list
        Ext.Ajax.request({
            url: "/main/config/",
            method: "GET",
            scope: me,
            success: me.onGetConfigList,
            failure: function() {
                NOC.error("Failed to get configs list");
            }
        });
    },
    // Process response with configs list
    onGetConfigList: function(response) {
        var me = this,
            data = Ext.decode(response.responseText);
        me.configListStore.loadData(data);
    },
    // Load config
    loadConfig: function(id) {
        var me = this;
        me.current = id || me.current;
        Ext.Ajax.request({
            url: "/main/config/" + me.current + "/",
            method: "GET",
            scope: me,
            success: me.onConfigLoad,
            failure: function() {
                NOC.error("Failed to get config");
                me.resetAll();
            }
        });
    },
    // New config selected
    onConfigSelect: function(combo, value) {
        var me = this;
        me.loadConfig(value);
    },
    // Config data received
    onConfigLoad: function(response) {
        var me = this,
            data = Ext.decode(response.responseText);
        me.searchField.setValue("");
        me.store.clearFilter(true);
        me.store.loadData(data);
        // Enable buttons
        me.saveButton.enable();
        me.searchField.enable();
    },
    // Clear all data
    resetAll: function() {

    },
    // SAVE button pressed
    onSave: function() {
        var me = this,
            data;
        // Prepare data
        data = me.store.data.filterBy(function(r) {
            return r.dirty === true;
        }).items.map(function(r) {
            return {
                section: r.data.section,
                key: r.data.key,
                value: r.data.value
            }
        });
        // Save
        Ext.Ajax.request({
            url: "/main/config/" + me.current + "/",
            method: "POST",
            scope: me,
            jsonData: data,
            success: function() {
                this.loadConfig();
                NOC.info("Config saved");
            },
            failure: function() {
                NOC.error("Failed to save config");
            }
        });
    },
    // Search
    onSearch: function(value) {
        var me = this;
        me.store.clearFilter(true);
        me.store.filterBy(function(r) {
            return (
                (value === "")
                    || (r.get("key").indexOf(value) != -1)
                    || (r.get("value").indexOf(value) != -1)
                    || (r.get("default").indexOf(value) != -1)
            );
        });
    }
});
