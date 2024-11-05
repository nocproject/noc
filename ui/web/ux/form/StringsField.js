//---------------------------------------------------
// Ext.ux.form.StringsField
//     ExtJS4 form field
//     Embedded grid
//---------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------
Ext.define("Ext.ux.form.StringsField", {
    extend: "Ext.form.FieldContainer",
    mixins: {
        field: 'Ext.form.field.Field'
    },
    alias: "widget.stringsfield",

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            fields: ["value"],
            data: []
        });

        me.addButton = Ext.create("Ext.button.Button", {
            text: __("Add"),
            glyph: NOC.glyph.plus,
            scope: me,
            handler: me.onAddRecord
        });

        me.appendButton = Ext.create("Ext.button.Button", {
            text: __("Append"),
            glyph: NOC.glyph.sign_in,
            scope: me,
            handler: Ext.pass(me.onAddRecord, true)
        });

        me.deleteButton = Ext.create("Ext.button.Button", {
            text: __("Delete"),
            glyph: NOC.glyph.minus,
            disabled: true,
            scope: me,
            handler: me.onDeleteRecord
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            layout: "fit",
            store: me.store,
            columns: [
                {
                    text: __("Value"),
                    dataIndex: "value",
                    flex: 1,
                    editor: "textfield",
                    renderer: NOC.render.htmlEncode
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
                        me.appendButton,
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
        if(me.value) {
            me.setValue(me.value);
        }
        me.callParent();
    },

    getValue: function() {
        var me = this,
            value = [];
        me.store.each(function(r) {
            value.push(r.get("value"));
        });
        return value;
    },

    setValue: function(v) {
        var me = this;
        if(v === undefined || v === "") {
            v = [];
        } else {
            v = v.map(function(x) {
                return {
                    value: x
                }
            });
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
    onAddRecord: function(self, evt, toEnd) {
        var me = this,
            rowEditing = me.grid.plugins[0],
            position = 0;
        if(toEnd) {
            position = me.grid.store.data.length;
        }
        rowEditing.cancelEdit();
        me.grid.store.insert(position, {value: ""});
        rowEditing.startEdit(position, 0);
        me.fireEvent("dirtychange", me);
    },
    //
    onDeleteRecord: function() {
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
        me.fireEvent("dirtychange", me);
    },
    //
    onCellEdit: function(editor, e) {
        var me = this;
        var cellEditor = e.grid.columns[e.colIdx].getEditor();
        if (cellEditor.rawValue) {
            e.record.set(e.field + "__label", cellEditor.rawValue);
        }
        me.fireEvent("dirtychange", me);
    },
});
