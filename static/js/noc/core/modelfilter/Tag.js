//---------------------------------------------------------------------
// NOC.core.modelfilter.Combo
// Combo lookup model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Tag");

Ext.define("NOC.core.modelfilter.Tag", {
    extend: "NOC.core.modelfilter.Base",
    require: ["NOC.core.TagsField"],

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            items: [
                {
                    xtype: "tagsfield",
                    name: me.name,
                    fieldLabel: me.title,
                    labelAlign: "top",
                    // createNewOnEnter: false,
                    // createNewOnBlur: false,
                    itemId: me.name,
                    width: 180,
                    listeners: {
                        select: {
                            scope: me,
                            fn: me.onChange
                        }
                    }
                }
            ]
        });
        me.callParent();
        me.tags = me.getComponent(me.name);
    },

    getFilter: function() {
        var me = this,
            v = me.tags.getValue(),
            r = {};
        if(v) {
            r[me.name + "__tags"] = v;
        }
        return r;
    }
});
