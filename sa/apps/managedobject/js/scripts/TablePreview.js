//---------------------------------------------------------------------
// TablePreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.TablePreview");

Ext.define("NOC.sa.managedobject.scripts.TablePreview", {
    extend: "NOC.sa.managedobject.scripts.ResultPreview",
    columns: [],
    search: false,

    initComponent: function() {
        var me = this,
            fields = [];
        me.searchFields = [];
        // Initialize store
        for(var i in me.columns) {
            var c = me.columns[i];
            if(c.dataIndex) {
                fields.push({
                    name: c.dataIndex,
                    type: "auto"
                });
                me.searchFields.push(c.dataIndex);
            }
        }
        me.store = Ext.create("Ext.data.Store", {
            model: null,
            fields: fields,
            data: []
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            columns: me.columns
        });

        Ext.apply(me, {
            items: [me.grid]
        });
        me.callParent();
        me.store.loadData(me.result || []);
    },
    //
    getToolbar: function() {
        var me = this,
            tb = me.callParent();
        if(me.search) {
            tb.push("-");
            tb.push(me.getSearchField());
        }
        return tb;
    },
    //
    getSearchField: function(cfg) {
        var me = this;
        me.searchField = Ext.create("Ext.form.field.Text", {
            name: "search_field",
            emptyText: "Search...",
            inputType: "search",
            hideLabel: true,
            width: 200,
            listeners: {
                change: {
                    fn: me.onSearch,
                    scope: me,
                    buffer: 200
                }
            }
        });
        return me.searchField;
    },
    //
    onSearch: function() {
        var me = this,
            text = me.searchField.getValue().toLowerCase();
        me.store.filterBy(function(record) {
            for(var i in me.searchFields) {
                var n = me.searchFields[i];
                if(String(record.get(n)).toLowerCase().indexOf(text) !== -1) {
                    return true;
                }
            }
            return false;
        });
    }
});
