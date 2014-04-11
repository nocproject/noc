//---------------------------------------------------------------------
// NOC.core.TreeFilterToolbar -
// Tags Field
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.TreeFilterToolbar");

Ext.define("NOC.core.TreeFilterToolbar", {
    extend: "Ext.toolbar.Toolbar",
    field: null,
    url: null,

    initComponent: function() {
        var me = this;

        me.currentFilter = null;
        Ext.apply(me, {
            items: []
        });
        me.addEvents("select");
        me.callParent();
        me.addCombo();
    },

    addCombo: function(parent) {
        var me = this,
            store = Ext.create("Ext.data.Store", {
                fields: ["id", "label"],
                proxy: Ext.create("Ext.data.RestProxy", {
                    url: me.url,
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
            combo = Ext.create("Ext.form.ComboBox", {
                nLevel: me.items.length,
                store: store,
                displayField: "label",
                valueField: "id",
                queryMode: "remote",
                queryParam: "__query",
                queryCaching: false,
                queryDelay: 200,
                forceSelection: true,
                minChars: 2,
                typeAhead: true,
                triggerAction: "all",
                listeners: {
                    scope: me,
                    select: me.onComboSelect,
                    specialkey: me.onComboSpecialKey
                }
            });
        if(parent) {
            Ext.apply(store.proxy.extraParams, {
                parent: parent
            });
        }
        me.add(combo);
        return combo;
    },
    //
    onComboSelect: function(combo, records, eOpts) {
        var me = this,
            v = combo.getValue();
        me.dropToLevel(combo.nLevel + 1);
        var c = me.addCombo(v);
        c.focus(true, true);  // @todo: Does not work
        me.currentFilter = v;
        me.fireEvent("select", me, v);
    },
    //
    dropToLevel: function(level) {
        var me = this;
        console.log("Drop to level", level);
        while(me.items.length > level) {
            console.log(me.items.length, level, me.items.length > level);
            me.remove(me.items.items[me.items.length - 1]);
        }
    },
    //
    onComboSpecialKey: function(combo, e) {
        var me = this;
        if(e.keyCode == e.ESC) {
            combo.clearValue();
            me.dropToLevel(combo.nLevel + 1);
            if(combo.nLevel === 0) {
                me.currentFilter = null;
            } else {
                me.currentFilter = me.items.items[combo.nLevel - 1].getValue();
            }
            me.fireEvent("select", me, me.currentFilter);
        }
    },
    getFilter: function() {
        var me = this,
            q = {};
        if(me.currentFilter) {
            q[me.field] = me.currentFilter;
        }
        return q;
    }
});