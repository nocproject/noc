//---------------------------------------------------------------------
// inv.inv Conduits form
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.conduits.ConduitsLayoutPanel");

Ext.define("NOC.inv.inv.plugins.conduits.ConduitsLayoutPanel", {
    extend: "Ext.panel.Panel",
    requires: [
        "NOC.core.Conduits"
    ],
    closable: false,
    layout: "fit",
    autoScroll: true,
    app: null,
    flex: 1,
    html: "Conduits layout",
    defaultScale: 4,

    initComponent: function() {
        var me = this;
        //
        me.createBlockButton = Ext.create("Ext.button.Button", {
            text: "Create Block",
            glyph: NOC.glyph.plus_circle,
            scope: me,
            handler: me.onCreateBlock,
            disabled: true
        });
        //
        me.conduitsView = Ext.create("Ext.container.Container", {
            autoScroll: true,
            region: "center"
        });
        //
        Ext.apply(me, {
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.createBlockButton
                ]
            }],
            items: me.conduitsView
        });
        me.callParent();
    },
    //
    drawConduits: function(items) {
        var me = this,
            data = NOC.core.Conduits.getConduits(items, me.defaultScale),
            dc = Ext.create("Ext.draw.Component", {
                viewBox: false,
                items: data,
                autoScroll: true
            });
        me.conduitsView.removeAll();
        me.conduitsView.add(dc);
    },
    //
    preview: function(record) {
        var me = this;
        me.drawConduits(record.get("conduits"));
        me.currentRecord = record;
        me.createBlockButton.setDisabled(false);
    },
    //
    onCreateBlock: function() {
        var me = this;
        Ext.create("NOC.inv.inv.plugins.conduits.CreateBlockForm", {
            app: me
        }).show();
    },
    //
    createBlock: function(config) {
        var me = this,
            data = NOC.core.Conduits.getBlock({
                count: parseInt(config.count),
                w: parseInt(config.w),
                d: parseInt(config.d),
                start: parseInt(config.start)
            });
        me.drawConduits(data);
        me.currentRecord.set("conduits", data);
        me.currentRecord.set("n_conduits", data.length);
    }
});
