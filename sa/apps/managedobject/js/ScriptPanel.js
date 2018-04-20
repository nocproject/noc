//---------------------------------------------------------------------
// sa.managedobject ScriptPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.ScriptPanel");

Ext.define("NOC.sa.managedobject.ScriptPanel", {
    extend: "NOC.core.ApplicationPanel",
    app: null,
    autoScroll: true,
    layout: "card",

    initComponent: function() {
        var me = this;

        me.currentObject = null;
        me.currentPreview = null;
        me.form = null;

        me.scriptStore = Ext.create("NOC.sa.managedobject.ScriptStore");

        me.searchField = Ext.create({
            xtype: "searchfield",
            name: "search_field",
            scope: me,
            handler: me.onSearch
        });

        me.scriptPanel = Ext.create("Ext.grid.Panel", {
            store: me.scriptStore,
            columns: [
                {
                    text: "Script",
                    dataIndex: "name",
                    flex: 1,
                    renderer: function(value, meta, record) {
                        if(record.get("has_input")) {
                            return value + "...";
                        } else {
                            return value;
                        }
                    }
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.getCloseButton(),
                        "-",
                        me.searchField
                    ]
                }
            ],
            listeners: {
                scope: me,
                celldblclick: me.onRunScript
            }
        });

        //
        Ext.apply(me, {
            items: [me.scriptPanel]
        });
        me.callParent();
        me.loadMask = new Ext.LoadMask(me, {msg: "Running task. Please wait ..."});
    },
    //
    preview: function(record, backItem) {
        var me = this;
        me.callParent(arguments);
        me.setTitle(record.get("name") + " scripts");
        Ext.Ajax.request({
            url: "/sa/managedobject/" + record.get("id") + "/scripts/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.scriptStore.loadData(data || []);
            },
            failure: function() {
                NOC.error("Failed to load data");
            }
        });
    },
    //
    onRunScript: function(grid, td, cellIndex, record, tr, rowIndex, e, eOpts) {
        var me = this,
            hi = record.get("has_input"),
            ri = record.get("require_input");
        me.currentPreview = record.get("preview");
        if(!hi || (e.altKey && !ri)) {
            me.runScript(record.get("name"));
        } else {
            me.showForm(record.get("name"), record.get("form"));
        }
    },
    //
    runScript: function(name, params) {
        var me = this;
        params = params || {};
        me.loadMask.show();
        Ext.Ajax.request({
            url: "/sa/managedobject/" + me.currentRecord.get("id") + "/scripts/" + name + "/",
            method: "POST",
            scope: me,
            jsonData: params,
            success: function(response) {
                var task = Ext.decode(response.responseText);
                me.waitResult(name, task);
            },
            failure: function() {
                me.loadMask.hide();
                NOC.error("Failed to run script");
            }
        });
    },
    //
    waitResult: function(name, task) {
        var me = this;
        Ext.Ajax.request({
            url: "/sa/managedobject/" + me.currentRecord.get("id") + "/scripts/" + name + "/" + task + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                if(data.ready) {
                    me.loadMask.hide();
                    if(data.result && data.result.result && data.result.result.code > 0 && data.result.result.text.length > 0) {
                        me.showError(name, data.result.result);
                    } else {
                        me.showResult(name, data.result);
                    }
                } else {
                    Ext.defer(Ext.bind(me.waitResult, me, [name, task]), 1000);
                }
            },
            failure: function() {
                me.loadMask.hide();
                NOC.error("Failed to run script");
            }
        });
    },
    //
    showResult: function(name, result) {
        var me = this,
            preview = Ext.create(me.currentPreview, {
            app: me,
            script: name,
            result: result.result
        });
        me.add(preview);
        me.getLayout().setActiveItem(1);
    },
    //
    showError: function(name, result) {
        var me = this,
            preview = Ext.create("NOC.sa.managedobject.scripts.ErrorPreview", {
                app: me,
                script: name,
                result: result
            });
        me.add(preview);
        me.getLayout().setActiveItem(1);
    },
    //
    showForm: function(name, items) {
        var me = this;
        me.form = Ext.create("Ext.form.Panel", {
            items: items,
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: "Close",
                            glyph: NOC.glyph.arrow_left,
                            scope: me,
                            handler: me.onFormClose
                        },
                        "-",
                        {
                            text: "Run",
                            glyph: NOC.glyph.play,
                            scope: me,
                            handler: Ext.bind(me.onFormRun, me, [name])
                        }
                    ]
                }
            ]
        });
        me.add(me.form);
        me.getLayout().setActiveItem(1);
    },
    //
    destroyForm: function() {
        var me = this;
        me.getLayout().setActiveItem(0);
        me.remove(me.form);
        me.form.close();
        me.form = null;
    },
    //
    onFormClose: function() {
        var me = this;
        me.destroyForm();
    },
    //
    onFormRun: function(name) {
        var me = this,
            params = me.form.getValues();
        me.destroyForm();
        me.runScript(name, params);
    },
    //
    onSearch: function(value) {
        var me = this;
        me.scriptStore.clearFilter(true);
        me.scriptStore.filterBy(function(record) {
            return record.get("name").indexOf(value) !== -1;
        }, me);
    }
});
