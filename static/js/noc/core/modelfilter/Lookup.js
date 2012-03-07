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
    url: null,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            items: [
                {
                    xtype: "combobox",
                    emptyText: "All",
                    allowBlank: true,
                    displayField: "label",
                    valueField: "id",
                    queryMode: "remote",
                    queryParam: "__query",
                    forceSelection: true,
                    minChars: 2,
                    typeAhead: true,
                    editable: true,
                    store: Ext.create("Ext.data.Store", {
                        fields: ["id", "label"],
                        proxy: Ext.create("Ext.data.RestProxy", {
                            url: me.url + "filter/" + me.name + "/",
                            pageParam: "__page",
                            startParam: "__start",
                            limitParam: "__limit",
                            sortParam: "__sort",
                            extraParams: {
                                "__format": "ext"
                            },
                            reader: {
                                type: "json",
                                root: "data",
                                totalProperty: "total",
                                successProperty: "success"
                            }
                        })
                    }),
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
        me.combo = me.items.items[0];
    },

    getFilter: function() {
        var me = this,
            v = me.combo.getValue(),
            r = {};
        if(v)
            r[this.name] = v;
        return r;
    }
});
