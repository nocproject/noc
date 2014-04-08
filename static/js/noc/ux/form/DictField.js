//---------------------------------------------------
// Ext.ux.form.DictField
//     ExtJS4 form field
//     Embedded grid
//---------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------
Ext.define("Ext.ux.form.DictField", {
    extend: "Ext.form.FieldContainer",
    mixins: {
        field: 'Ext.form.field.Field'
    },
    alias: "widget.dictfield",

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            fields: ["key", "value"],
            data: []
        });

        me.addButton = Ext.create("Ext.button.Button", {
            text: "Add",
            glyph: NOC.glyph.plus,
            scope: me,
            handler: me.onAdd
        });

        me.deleteButton = Ext.create("Ext.button.Button", {
            text: "Delete",
            glyph: NOC.glyph.minus,
            disabled: true,
            scope: me,
            handler: me.onDelete
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            layout: "fit",
            store: me.store,
            columns: [
                {
                    text: "Key",
                    dataIndex: "key",
                    width: 150,
                    editor: "textfield",
                    renderer: "htmlEncode"
                },
                {
                    text: "Value",
                    dataIndex: "value",
                    flex: 1,
                    editor: "textfield",
                    renderer: "htmlEncode"
                }
            ],
            plugins: [
                Ext.create("Ext.grid.plugin.CellEditing", {
                    clicksToEdit: 2,
                    listeners: {
                        scope: me,
                        edit: me.onCellEdit
                    }
                })
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.addButton,
                        me.deleteButton
                    ]
                }
            ],
            listeners: {
                scope: me,
                select: me.onSelect
            }
        });

        Ext.apply(me, {
            items: [
                me.grid
            ]
        });
        me.currentSelection = undefined;
        me.callParent();
    },

    getValue: function() {
        var me = this,
            value = {};
        me.store.each(function(r) {
            value[r.get("key")] = r.get("value");
        });
        return value;
    },

    setValue: function(v) {
        var me = this,
            nv = [];
        if(v === undefined || v === "") {
            v = [];
        } else {
            v = v || {};
            var keys = Object.keys(v);
            for(var i in keys) {
                var k = keys[i];
                nv.push({
                    key: k,
                    value: v[k]
                });
            }
            v = nv;
        }
        me.store.loadData(v);
        return me.mixins.field.setValue.call(me, v);
    },
    //
    onSelect: function(grid, record, index) {
        var me = this;
        me.currentSelection = index;
        me.deleteButton.setDisabled(false);
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
        } else {
            me.deleteButton.setDisabled(true);
        }
    },
    //
    onCellEdit: function(editor, e) {
        var me = this,
            editor = e.grid.columns[e.colIdx].getEditor();
        if(editor.rawValue) {
            e.record.set(e.field + "__label", editor.rawValue);
        }
    }
});
