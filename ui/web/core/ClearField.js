//---------------------------------------------------------------------
// NOC.core.ClearField -
// Lookup form field
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ClearField");

Ext.define("NOC.core.ClearField", {

    toDefaultValueString: function(me) {
        me.setValue(me._getDefaultValue(me));
    },

    showClearTrigger: function(me) {
        var defaultValue = this._getDefaultValue(me);
        var newValue = this._getNewValue(me);

        if(me.getTrigger('clear').hidden && newValue !== defaultValue) {
            me.getTrigger('clear').show();
            me.updateLayout();
        }

        if(newValue === defaultValue) {
            me.getTrigger('clear').hide();
            me.updateLayout();
        }
    },

    _getNewValue: function(me) {
        if(me.valueCollection && Ext.isFunction(me.valueCollection.getRange)) { // Combobox
            return me.valueCollection.getRange()[0].get(me.valueField);
        }
        return me.value;
    },

    _getDefaultValue: function(me) {
        var application = me.findParentBy(function(p) {
                return p.model;
            }),
            defaultValue = "";

        if(application) {
            defaultValue = Ext.create(application.model).fields.filter(function(f) {
                return f.name === me.name
            })[0].defaultValue || "";
        }
        return defaultValue;
    }
});