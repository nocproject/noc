//---------------------------------------------------
// Ext.ux.form.GridField
//     ExtJS4 form field
//     Embedded grid
//---------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------
Ext.define("Ext.ux.form.GridField", {
    extend: "Ext.form.field.Base",
    alias: "widget.gridfield",
    fieldSubTpl: "<div class='noc-gridfield'></div>",
    width: 500,
    height: 200,
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
        me.callParent();
    },

    onRender: function(ct, position) {
        var me = this;
        me.callParent([ct, position]);
        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            width: me.width,
            height: me.height,
            renderTo: Ext.query(".noc-gridfield", this.el.dom)[0],
            columns: me.columns,
            plugins: [
                Ext.create("Ext.grid.plugin.RowEditing", {
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
        v = v || [];
        me.store.loadData(v);
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
