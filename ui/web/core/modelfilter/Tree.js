//---------------------------------------------------------------------
// NOC.core.modelfilter.Combo
// Combo lookup model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Tree");

Ext.define("NOC.core.modelfilter.Tree", {
    extend: "NOC.core.modelfilter.Base",
    lookup: null,  // module.app
    referrer: null, // Referrer application id

    requires: [],

    initComponent: function() {
        var me = this,
            wn = "NOC." + me.lookup + ".TreeCombo",
            tree = Ext.create(wn, {
                labelAlign: "top",
                fieldLabel: me.title,
                width: 180,
                restUrl: '/' + me.lookup.replace('.', '/'),
                listeners: {
                    scope: me,
                    clear: me.onChange,
                    select: me.onChange,
                    change: me.onChange
                }
            });
        Ext.apply(me, {
            items: [tree]
        });
        me.callParent();
        me.tree = tree;
    },

    getFilter: function() {
        var me = this,
            r = {},
            v;

        if(me.tree.fieldValue) {
            v = me.tree.getFieldValue().id;
            if(v) {
                r[me.name] = v;
            }
            return r;
        }
        return r;
    }
});
