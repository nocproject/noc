//---------------------------------------------------
// Ext.ux.form.GridField
//     ExtJS4 form field
//     Embedded grid
//---------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------
Ext.define("Ext.ux.form.GridField", {
    extend: "Ext.form.FieldContainer",
    mixins: {
        field: 'Ext.form.field.Field'
    },
    alias: "widget.gridfield",
    columns: [],

    initComponent: function() {
        var me = this;

        me.fields = me.columns.map(function(v) {
            return v.dataIndex;
        });
        me.store = Ext.create("Ext.data.Store", {
            fields: me.fields,
            data: []
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            layout: "fit",
            store: me.store,
            columns: me.columns,
            plugins: [
                Ext.create("Ext.grid.plugin.CellEditing", {
                    clicksToEdit: 2
                })
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: "Add",
                            glyph: NOC.glyph.plus,
                            scope: me,
                            handler: me.onAdd
                        },
                        {
                            text: "Delete",
                            glyph: NOC.glyph.minus,
                            scope: me,
                            handler: me.onDelete
                        }
                    ]
                }
            ]
        });

        Ext.apply(me, {
            items: [
                me.grid
            ]
        });
        me.callParent();
    },

    getValue: function() {
        var me = this,
            records = [];
        me.store.each(function(r) {
            var d = {};
            Ext.each(me.fields, function(f) {
                d[f] = r.get(f);
            });
            records.push(d);
        });
        return records;
    },

    setValue: function(v) {
        var me = this;
        if(v === undefined || v === "") {
            v = [];
        } else {
            v = v || [];
        }
        me.store.loadData(v);
        return me.mixins.field.setValue.call(me, v);
    },

    //
    onAdd: function() {
        var me = this,
            rowEditing = me.grid.plugins[0];
        rowEditing.cancelEdit();
        me.grid.store.insert(0, {});
        rowEditing.startEdit(0, 0);
    },
    //
    onDelete: function() {
        var me = this,
            sm = me.grid.getSelectionModel(),
            rowEditing = me.grid.plugins[0];
        rowEditing.cancelEdit();
        me.grid.store.remove(sm.getSelection());
        if(me.grid.store.getCount() > 0) {
            sm.select(0);
        }
    }
});
