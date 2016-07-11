//---------------------------------------------------------------------
// NOC.core.modelfilter.Favorites
// Favorites model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Favorites");

Ext.define("NOC.core.modelfilter.Favorites", {
    extend: "NOC.core.modelfilter.Base",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            items: [
                {
                    xtype: "button",
                    glyph: NOC.glyph.star,
                    cls: "noc-starred",
                    toggleGroup: "favgroup",
                    scope: me,
                    handler: function(button, e) {
                        me._value = button.pressed ? true : undefined;
                        me.onChange();
                    }
                },
                {
                    xtype: "button",
                    glyph: NOC.glyph.star,
                    cls: "noc-unstarred",
                    toggleGroup: "favgroup",
                    scope: me,
                    handler: function(button, e) {
                        me._value = button.pressed ? false : undefined;
                        me.onChange();
                    }
                }
            ]
        });
        me.callParent();
        me._value = undefined;
    },

    getFilter: function() {
        var me = this,
            r = {};
        if(me._value !== undefined)
            r[me.name] = me._value;
        return r;
    }
});
