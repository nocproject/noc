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
    rows: this.rows || 3,
    timerHandler: undefined,
    initComponent: function() {
        var me = this;

        // me.rows = me.rows || 3;
        me.fields = Ext.clone(me.items).map(function(item) {
            return Ext.Object.merge(item, {isListForm: true})
        });

        me.addButtonEnd = Ext.create("Ext.button.Button", {
            text: __("Append"),
            glyph: NOC.glyph.plus,
            scope: me,
            handler: Ext.pass(me.onAddRecord, true)
        });

        me.addButton = Ext.create("Ext.button.Button", {
            text: __("Insert"),
            glyph: NOC.glyph.indent,
            scope: me,
            handler: Ext.pass(me.onAddRecord)
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

        me.panel = Ext.create("Ext.form.Panel", {
            scrollable: 'vertical',
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.addButton,
                        me.addButtonEnd,
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
        if(!Ext.isEmpty(v) && me.timerHandler) {
            clearTimeout(me.timerHandler);
            me.timerHandler = undefined;
        }
        if(me.panel.items.length) {
            me.panel.removeAll();
        }
        Ext.each(v, me.createForm, me);
        me.currentSelection = undefined;
        me.disableButtons(true);
    },
    reset: function() {
        var me = this;
        me.timerHandler = setTimeout(function(scope) {
            scope.removeAll();
        }, 750, me.panel);
    },
    onAddRecord: function() {
        var me = this, index;
        if(Ext.isBoolean(arguments[0]) && arguments[0]) {
            // to end
            index = me.panel.items.length;
        } else {
            index = me.panel.items.findIndexBy(function(i) {
                return i.itemId === me.currentSelection
            }, me) + 1;
        }
        me.createForm(undefined, index);
    },
    onDeleteRecord: function() {
        var me = this;
        // remove by itemId
        me.panel.remove(me.currentSelection);
        me.currentSelection = undefined;
        me.disableButtons(true);
    },
    onCloneRecord: function() {
        var me = this;
        me.createForm(me.panel.getComponent(me.currentSelection).getValues());
    },
    onMoveDown: function() {
        var me = this, index, yPosition, yStep;
        index = me.panel.items.findIndexBy(function(i) {
            return i.itemId === me.currentSelection
        }, me);
        if(index < me.panel.items.getCount() - 1) {
            me.panel.moveAfter(me.panel.items.get(index), me.panel.items.get(index + 1));
            yStep = me.panel.getScrollable().getMaxPosition().y / (me.panel.items.length - me.rows);
            yPosition = me.panel.getScrollable().getPosition().y;
            me.panel.getScrollable().scrollTo(null, yPosition + yStep, false);
        }
    },
    onMoveUp: function() {
        var me = this, index, yPosition, yStep;
        index = me.panel.items.findIndexBy(function(i) {
            return i.itemId === me.currentSelection
        }, me);
        if(index > 0) {
            me.panel.moveBefore(me.panel.items.get(index), me.panel.items.get(index - 1));
            if(index > me.rows) {
                yStep = me.panel.getScrollable().getMaxPosition().y / (me.panel.items.length - me.rows);
                yPosition = me.panel.getScrollable().getPosition().y;
                me.panel.getScrollable().scrollTo(null, yPosition - yStep, false);
            }
        }
    },
    createForm: function(record, index) {
        var me = this, formPanel, itemId;
        if(index === undefined) {
            index = me.panel.items.getCount();
        }
        itemId = Ext.id(null, "list-form-");
        formPanel = Ext.create('Ext.form.Panel', {
            itemId: itemId,
            items: me.fields,
            defaults: {
                margin: "0 30 0 10"
            },
            listeners: {
                scope: me,
                focusenter: function(self) {
                    var me = this;
                    // reset selected label
                    me.panel.items.each(function(panel) {
                        panel.setBodyStyle("border-left-width", "1px");
                        panel.setBodyStyle("margin-left", "5px")
                    });
                    me.selected(self);
                    me.currentSelection = self.itemId;
                    me.disableButtons(false);
                },
                afterrender: function(self) {
                    var me = this;
                    me.panel.setMaxHeight(self.getHeight() * me.rows);
                }
            }
        });
        formPanel.setBodyStyle("margin-left", "5px");
        if(record != null) {
            formPanel.form.setValues(record);
        }
        me.panel.insert(index, formPanel);
        formPanel.items.get(0).focus();
    },
    disableButtons: function(arg) {
        var me = this;
        me.addButton.setDisabled(arg);
        me.deleteButton.setDisabled(arg);
        me.cloneButton.setDisabled(arg);
    },
    selected: function(panel) {
        panel.setBodyStyle("border-left-width", "6px");
        panel.setBodyStyle("margin-left", "0px")
    }
});