//---------------------------------------------------------------------
// NOC.core.ComboField -
// Combo form field with clear trigger
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ComboField");

Ext.define("NOC.core.ComboField", {
    extend: "Ext.form.field.ComboBox",
    alias: 'widget.nocComboField',

    mixins: [
        "NOC.core.ClearField"
    ],

    triggers: {
        clear: {
            weight: 1,
            cls: Ext.baseCSSPrefix + 'form-clear-trigger',
            hidden: true,
            handler: 'toDefaultValueString',
            scope: 'this'
        },
        picker: {
            weight: 2,
            handler: 'onTriggerClick',
            scope: 'this'
        }
    },
    // override private method, don't use change listener
    updateValue: function() {
        var me = this;
        me.showClearTrigger(me);
        me.callParent();
    }
});