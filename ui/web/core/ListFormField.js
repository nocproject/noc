//---------------------------------------------------------------------
// Form Field
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.FormField");

Ext.define("NOC.core.ListFormField", {
    extend: "Ext.form.FieldContainer",
    alias: "widget.listform",
    mixins: {
        field: 'Ext.form.field.Field'
    },
    items: [],
    isSelectedPrefix: "<*>",
    timerHander: undefined,
    initComponent: function() {
        var me = this;

        me.fields = Ext.clone(me.items);

        me.addButton = Ext.create("Ext.button.Button", {
            text: __("Add"),
            glyph: NOC.glyph.plus,
            scope: me,
            handler: me.onAddRecord
        });

        me.deleteButton = Ext.create("Ext.button.Button", {
            text: __("Delete"),
            glyph: NOC.glyph.minus,
            disabled: true,
            scope: me,
            handler: me.onDeleteRecord
        });

        me.cloneButton = Ext.create("Ext.button.Button", {
            text: __("Clone"),
            glyph: NOC.glyph.copy,
            disabled: true,
            scope: me,
            handler: me.onCloneRecord
        });

        me.moveUpButton = Ext.create("Ext.button.Button", {
            text: __("Move Up"),
            glyph: NOC.glyph.caret_up,
            scope: me,
            handler: me.onMoveUp
        });

        me.moveDownButton = Ext.create("Ext.button.Button", {
            text: __("Move Down"),
            glyph: NOC.glyph.caret_down,
            scope: me,
            handler: me.onMoveDown
        });

        me.mainConfig = {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.addButton,
                        me.deleteButton,
                        "-",
                        me.cloneButton,
                        "-",
                        me.moveUpButton,
                        me.moveDownButton
                    ]
                }
            ],
            items: []
        };
        me.panel = Ext.create("Ext.form.Panel", {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.addButton,
                        me.deleteButton,
                        "-",
                        me.cloneButton,
                        "-",
                        me.moveUpButton,
                        me.moveDownButton
                    ]
                }
            ],
            items: []
        });
        Ext.apply(me, {
            items: [
                me.panel
            ]
        });
        me.currentSelection = undefined;
        me.callParent();
    },
    getValue: function() {
        var me = this,
            records = [];
        me.panel.items.each(function(panel) {
            records.push(panel.form.getValues())
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
        if(!Ext.isEmpty(v) && me.timerHander) {
            clearTimeout(me.timerHander);
            me.timerHander = undefined;
        }
        if(me.panel.items.length) {
            me.panel.removeAll();
        }
        Ext.each(v, me.createForm, me);
        this.disableButtons(me);
    },
    reset: function() {
        var me = this;
        me.timerHander = setTimeout(function(scope) {
            scope.removeAll();
        }, 750, me.panel);
    },
    onAddRecord: function() {
        var me = this;
        me.createForm();
    },
    onDeleteRecord: function() {
        var me = this;
        // remove by itemId
        me.panel.remove(me.currentSelection);
        me.disableButtons();
    },
    onCloneRecord: function() {
        var me = this;
        me.createForm(me.panel.getComponent(me.currentSelection).getValues());
    },
    onMoveDown: function() {
        var me = this, index;
        index = me.panel.items.findIndexBy(function(i) {
            return i.itemId === me.currentSelection
        }, me);
        if(index < me.panel.items.getCount() - 1) {
            me.panel.moveAfter(me.panel.items.get(index), me.panel.items.get(index + 1));
        }
    },
    onMoveUp: function() {
        var me = this, index;
        index = me.panel.items.findIndexBy(function(i) {
            return i.itemId === me.currentSelection
        }, me);
        if(index > 0) {
            me.panel.moveBefore(me.panel.items.get(index), me.panel.items.get(index - 1));
        }
    },
    createForm: function(record, index) {
        var me = this, formPanel, itemId;
        if(!index) {
            index = me.panel.items.getCount();
        }
        itemId = me.id + '-' + index;
        formPanel = Ext.create('Ext.form.Panel', {
            itemId: itemId,
            items: me.fields,
            defaults: {
                margin: "0 0 0 10"
            },
            listeners: {
                scope: me,
                focusenter: function(self) {
                    var me = this, label;
                    // reset selected label
                    me.panel.items.each(function(panel) {
                        var l = panel.items.get(0).getFieldLabel().replace(me.isSelectedPrefix, "");
                        panel.items.get(0).setFieldLabel(l);
                    });
                    label = self.items.get(0).getFieldLabel();
                    self.items.get(0).setFieldLabel(me.isSelectedPrefix + label);
                    me.currentSelection = self.itemId;
                    me.deleteButton.setDisabled(false);
                    me.cloneButton.setDisabled(false);
                }
            }
        });
        formPanel.form.setValues(record);
        me.panel.add(formPanel);
        formPanel.items.get(0).focus();
    },
    disableButtons: function() {
        var me = this;
        me.currentSelection = undefined;
        me.deleteButton.setDisabled(true);
        me.cloneButton.setDisabled(true);
    }
});