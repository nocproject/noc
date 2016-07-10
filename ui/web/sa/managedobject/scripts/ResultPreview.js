//---------------------------------------------------------------------
// ResultPreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ResultPreview");

Ext.define("NOC.sa.managedobject.scripts.ResultPreview", {
    extend: "Ext.panel.Panel",
    app: undefined,
    result: undefined,
    script: undefined,
    layout: "fit",

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: me.getToolbar()
                }
            ]
        });
        // Change title
        me.appTitle = me.app.title;
        me.app.setTitle(me.app.currentRecord.get("name") + " " + me.script);
        me.callParent();
    },
    /*
     * Returns a list of toolbar items
     */
    getToolbar: function() {
        var me = this;
        return [me.getCloseButton()]
    },

    getCloseButton: function(cfg) {
        var me = this,
            opts = {
                text: "Close",
                glyph: NOC.glyph.arrow_left,
                scope: me,
                handler: me.onClose
            };
        Ext.apply(opts, cfg || {});
        return Ext.create("Ext.button.Button", opts);
    },

    onClose: function() {
        var me = this;
        me.app.getLayout().setActiveItem(0);
        me.app.remove(me);
        me.close();
        me.app.setTitle(me.appTitle);
    }
});
