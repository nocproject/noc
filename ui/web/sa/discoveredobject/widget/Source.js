//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.widget.Source");

Ext.define("NOC.sa.discoveredobject.widget.Source", {
    extend: "Ext.form.field.Base",
    alias: "widget.sourcefield",
    layout: "fit",
    combineErrors: true,
    msgTarget: "side",
    fieldSubTpl: [
        "<div></div>",
    ],
    afterRender: function() {
        this.createSegmentedButton();
        if(this.value) {
            this.buttons.setValue(this.value);
        }
        this.callParent(arguments);
    },
    createSegmentedButton: function() {
        var me = this;

        me.buttons = Ext.create("Ext.button.Segmented", {
            renderTo: this.bodyEl,
            allowMultiple: true,
            vertical: false, // True to align the buttons vertically
            items: this.items,
            width: "100%",
            listeners: {
                toggle: function() {
                    me.value = me.rawValue = me.buttons.getValue();
                    me.fireEvent("change", me, me.value);
                }
            }
        });
    },
    getValue: function() {
        return this.buttons ? this.buttons.getValue() : [];
    },
    setValue: function(value) {
        if(this.buttons) {
            this.buttons.setValue(value);
        }
        this.value = this.rawValue = value;
    }
});