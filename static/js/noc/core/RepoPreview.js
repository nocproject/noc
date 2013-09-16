//---------------------------------------------------------------------
// NOC.core.RepoPreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.RepoPreview");

Ext.define("NOC.core.RepoPreview", {
    extend: "NOC.core.ApplicationPanel",
    msg: "",
    layout: "fit",
    syntax: null,
    restUrl: null,

    initComponent: function() {
        var me = this;

        me.revCombo = Ext.create("Ext.form.ComboBox", {
            fieldLabel: "Version",
            labelWidth: 45,
            width: 200,
            queryMode: "local",
            displayField: "ts_label",
            valueField: "id",
            store: Ext.create("Ext.data.Store", {
                fields: [
                    {
                        name: "id",
                        type: "auto"
                    },
                    {
                        name: "ts",
                        type: "date"
                    },
                    {
                        name: "ts_label",
                        mapping: "ts",
                        convert: function(v, record) {
                            return NOC.render.DateTime(record.get("ts"));
                        }
                    }
                ],
                data: []
            }),
            listeners: {
                scope: me,
                select: me.onSelectRev,
                specialkey: me.onRevSpecialKey
            }
        });

        me.diffCombo = Ext.create("Ext.form.ComboBox", {
            fieldLabel: "Compare",
            disabled: true,
            labelWidth: 45,
            width: 200,
            queryMode: "local",
            displayField: "ts_label",
            valueField: "id",
            store: Ext.create("Ext.data.Store", {
                fields: [
                    {
                        name: "id",
                        type: "auto"
                    },
                    {
                        name: "ts",
                        type: "date"
                    },
                    {
                        name: "ts_label",
                        mapping: "ts",
                        convert: function(v, record) {
                            return NOC.render.DateTime(record.get("ts"));
                        }
                    }
                ],
                data: []
            }),
            listeners: {
                scope: me,
                select: me.onSelectDiff,
                specialkey: me.onDiffSpecialKey
            }
        });

        Ext.apply(me, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    {
                        itemId: "close",
                        text: "Close",
                        glyph: NOC.glyph.arrow_left,
                        scope: me,
                        handler: me.onClose
                    },
                    "-",
                    me.revCombo,
                    me.diffCombo
                ]
            }],
            items: [{
                xtype: "container",
                autoScroll: true,
                padding: 4
            }]
        });
        me.callParent();
        //
        me.urlTemplate = Handlebars.compile(me.restUrl);
        me.titleTemplate = Handlebars.compile(me.previewName);
    },
    //
    preview: function(record, backItem) {
        var me = this;
        me.callParent(arguments);
        // me.rootUrl = Ext.String.format(me.restUrl, record.get("id"));
        me.rootUrl = me.urlTemplate(record.data);
        me.setTitle(me.titleTemplate(record.data));
        me.requestText();
        me.requestRevisions();
    },
    //
    requestText: function() {
        var me = this;
        Ext.Ajax.request({
            url: me.rootUrl,
            method: "GET",
            scope: me,
            success: function(response) {
                me.renderText(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error("Failed to get text");
            }
        });
    },
    //
    requestRevisions: function() {
        var me = this;
        Ext.Ajax.request({
            url: me.rootUrl + "revisions/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.revCombo.store.loadData(data);
                me.diffCombo.store.loadData(data);
            },
            failure: function() {
                NOC.error("Failed to get revisions");
            }
        });
    },
    //
    requestRevision: function(rev) {
        var me = this;
        Ext.Ajax.request({
            url: me.rootUrl + rev + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                me.renderText(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error("Failed to get text");
            }
        });
    },
    //
    requestDiff: function(rev1, rev2) {
        var me = this;
        Ext.Ajax.request({
            url: me.rootUrl + rev1 + "/" + rev2 + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                me.renderText(Ext.decode(response.responseText), "diff");
            },
            failure: function() {
                NOC.error("Failed to get diff");
            }
        });
    },
    //
    renderText: function(text, syntax) {
        var me = this;
        syntax = syntax || me.syntax;
        NOC.SyntaxHighlight.highlight(me.items.first(), text, syntax);
    },
    //
    onSelectRev: function(combo, records, eOpts) {
        var me = this;
        me.requestRevision(records[0].get("id"));
        me.diffCombo.setDisabled(false);
    },
    //
    onSelectDiff: function(combo, records, eOpts) {
        var me = this;
        me.requestDiff(
            me.revCombo.getValue(),
            me.diffCombo.getValue()
        );
    },
    //
    onRevSpecialKey: function(combo, evt, opts) {
        var me = this;
        if(evt.getKey() == evt.ESC) {
            combo.clearValue();
        }
    },
    //
    onDiffSpecialKey: function(combo, evt, opts) {
        var me = this;
        if(evt.getKey() == evt.ESC) {
            combo.clearValue();
        }
    }
});
