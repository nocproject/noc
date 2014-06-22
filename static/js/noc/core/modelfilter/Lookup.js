//---------------------------------------------------------------------
// NOC.core.modelfilter.Combo
// Combo lookup model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Lookup");

Ext.define("NOC.core.modelfilter.Lookup", {
    extend: "NOC.core.modelfilter.Base",
    lookup: null,  // module.app
    referrer: null, // Referrer application id

    initComponent: function() {
        var me = this,
            wn = "NOC." + me.lookup + ".LookupField",
            w = Ext.create(wn, {
                fieldLabel: me.title,
                labelAlign: "top",
                width: 180,
                query: {
                    "id__referred": me.referrer + "__" + me.name
                },
                listeners: {
                    scope: me,
                    select: me.onChange,
                    clear: me.onChange,
                    blur: me.onChange
                }
            });

        Ext.apply(me, {
            items: [w]
        });
        me.callParent();
        me.combo = w;
    },

    getFilter: function() {
        var me = this,
            v = me.combo.getValue(),
            r = {};
        if(v)
            r[me.name] = v;
        return r;
    }
});
