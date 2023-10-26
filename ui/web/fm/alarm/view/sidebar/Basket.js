//---------------------------------------------------------------------
// core.basket widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.sidebar.Basket");

Ext.define("NOC.fm.alarm.view.sidebar.Basket", {
    extend: "Ext.form.field.ComboBox",
    alias: "widget.fm.basket",
    fieldLabel: __("Basket"),
    displayField: "label",
    valueField: "id",

    triggers: {
        clear: {
            cls: 'x-form-clear-trigger',
            hidden: true,
            weight: -1,
            handler: function(field) {
                field.setValue(null);
                // field.fireEvent("select", field);
            }
        },
        create: {
            cls: "x-form-plus-trigger",
            hidden: false,
            handler: function(field) {
                field.fireEvent("fmAlarmNewBasket", field);
            }
        },
        update: {
            cls: "x-form-edit-trigger",
            hidden: true,
            handler: function(field) {
                field.fireEvent("fmAlarmUpdateBasket", field);
            }
        }
    },
    listeners: {
        change: function(field, value) {
            field.fireEvent("fmAlarmUpdateOpenBasket", field);
            this.showTriggers(value);
        }
    },

    showTriggers: function(value) {
        var me = this,
            process = function(value) {
                me.getTrigger("create").hide();
                me.getTrigger("clear").show();
                if(value == null || value === "") {
                    if(!me.hideTriggerCreate) me.getTrigger("create").show();
                    me.getTrigger("clear").hide();
                    me.getTrigger("update").hide();
                    return;
                }
                if(!me.hideTriggerUpdate) me.getTrigger("update").show();
            };

        process(value);
    },

    store: {
        data: [
            {
                id: "63861d16c751016844292f5d",
                label: __("Basket1"),
                conditions: [
                    {
                        managed_object: "mmmm",
                        address: "xxxx",
                        ip: null
                    },
                    {
                        managed_object: "nnnn",
                        address: "yyyy",
                        ip: "10.1.1.1"
                    }
                ]
            },
            {
                id: "63861d16c751016844292f5c",
                label: __("Basket2"),
                conditions: [
                    {
                        managed_object: "22-",
                        address: "wwww",
                        ip: null
                    }
                ]
            },
            {
                id: "63861d16c751016844292f5e",
                label: __("Basket3"),
                conditions: [
                    {
                        managed_object: "15-",
                        address: "qqqq",
                        ip: null
                    }
                ]
            }
        ]
    }

})