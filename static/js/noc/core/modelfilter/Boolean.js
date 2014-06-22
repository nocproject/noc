//---------------------------------------------------------------------
// NOC.core.modelfilter.Boolean
// Boolean model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Boolean");

Ext.define("NOC.core.modelfilter.Boolean", {
    extend: "NOC.core.modelfilter.Base",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            layout: "hbox",
            items: [
                {
                    xtype: "button",
                    glyph: NOC.glyph.check,
                    cls: "noc-yes",
                    toggleGroup: "boolgroup",
                    scope: me,
                    handler: function (button, e) {
                        me._value = button.pressed ? "4" : undefined;
                        me.onChange();
                    }
                },
                {
                    xtype: "button",
                    glyph: NOC.glyph.times,
                    cls: "noc-no",
                    toggleGroup: "boolgroup",
                    scope: me,
                    handler: function (button, e) {
                        me._value = button.pressed ? "6" : undefined;
                        me.onChange();
                    }
                },
                {
                    xtype: "container",
                    html: Ext.util.Format.htmlEncode(me.title),
                    padding: 4
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
