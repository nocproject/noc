//---------------------------------------------------------------------
// NOC.core.TextField -
// Text form field with clear trigger
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.TextField");

Ext.define("NOC.core.TextField", {
    extend: "Ext.form.field.Text",
    alias: 'widget.nocTextField',

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
        }
    },
    // override private method, don't want to use change listener
    publishValue: function() {
        var me = this;
        me.showClearTrigger(me);
        me.callParent();
    }
});