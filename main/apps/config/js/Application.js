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
        me.grid = Ext.create("Ext.grid.Panel", {
            border: false,
            autoScroll: true,
            stateful: true,
            stateId: "main.config-grid",
            store: me.store,
            features: [{
                ftype: "grouping",
                groupHeaderTpl: "[{name}]"
            }],
            selType: "rowmodel",
            plugins: [
                Ext.create("Ext.grid.plugin.RowEditing", {
                    clicksToEdit: 1
                })
            ],
            columns: [
                {
                    text: "Section",
                    dataIndex: "section",
                    hidden: true
                },
                {
                    text: "Key",
                    dataIndex: "key",
                    width: 300
                },
                {
                    text: "Default",
                    dataIndex: "default",
                    flex: 1
                },
                {
                    text: "Value",
                    dataIndex: "value",
                    editor: "textfield",
                    flex: 1
                }
            ],
            tbar: [
                "Config:",
                {
                    xtype: "combobox",
                    name: "config",
                    itemId: "config",
                    width: 150,
                    emptyText: "Select Config ...",
                    store: me.configListStore,
                    queryMode: "local",
                    displayField: "name",
                    valueField: "id",
                    listeners: {
                        change: {
                            scope: me,
                            fn: me.onConfigSelect
                        }
                    }
                },
                {
                    xtype: "textfield",
                    name: "search",
                    itemId: "search",
                    inputType: "search",
                    disabled: true,
                    emptyText: "Search ...",
                    listeners: {
                        change: {
                            scope: me,
                            fn: me.onSearch
                        }
                    }
                },
                "-",
                {
                    itemId: "save",
                    name: "save",
                    text: "Save",
                    glyph: NOC.glyph.save,
                    disabled: true,
                    scope: me,
                    handler: me.onSave
                }
            ]
        });
        Ext.apply(me, {
            items: [
                me.grid
            ]
        });
        me.callParent();

        var gt = me.grid.dockedItems.items[1];
        me.searchField = gt.getComponent("search");
        me.saveButton = gt.getComponent("save");
        me.current = null;
        console.log(gt, me);
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
        me.current = id || me.current
        Ext.Ajax.request({
            url: "/main/config/" + me.current + "/",
            method: "GET",
            scope: me,
            success: me.onConfigLoad,
            failure: function() {
                NOC.error("Failed to get config");
                this.resetAll();
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
        // @todo: Reset search
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
    onSearch: function(field, value) {
        var me = this;
        me.store.filterBy(function(r) {
            return (
                (value === "")
                    || (r.data.key.indexOf(value) != -1)
                    || (r.data.value.indexOf(value) != -1)
                    || (r.data.default.indexOf(value) != -1));
        });
    }
});
