//---------------------------------------------------------------------
// NOC.core.modelfilter.AFI
// AFI model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.AFI");

Ext.define("NOC.core.modelfilter.AFI", {
    extend: "NOC.core.modelfilter.Base",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            layout: "hbox",
            items: [
                {
                    xtype: "button",
                    text: "IPv4",
                    toggleGroup: "afigroup",
                    scope: me,
                    handler: function(button, e) {
                        me._value = button.pressed ? "4" : undefined;
                        me.onChange();
                    }
                },
                {
                    xtype: "button",
                    text: "IPv6",
                    toggleGroup: "afigroup",
                    scope: me,
                    handler: function(button, e) {
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
        var r = {};
        if(this._value !== null)
            r[this.name] = this._value;
        return r;
    }
});
