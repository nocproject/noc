//---------------------------------------------------------------------
// sa.runcommands application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.runcommands.Application");

Ext.define("NOC.sa.runcommands.Application", {
    extend: "NOC.core.SAApplication",

    getConfigPanel: function () {
        var me = this;

        me.commandsField = Ext.create({
            xtype: "textarea",
            fieldLabel: __("Commands"),
            labelAlign: "top",
            width: '100%',
            height: 700,
            scrollable: true,
            padding: 4,
            // ???
            componentId: "commands",
            itemId: 'commands',
            listeners: {
                scope: me,
                change: function (field, newValue, oldValue) {
                    me.runButton.setDisabled(
                        !newValue
                    );
                }
            }
        });

        return Ext.create("Ext.panel.Panel", {
            activeItem: 'commands',
            border: false,
            items: [
                me.commandsField
            ]
        });
    },

    getResultPanel: function() {
        var me = this,
            text;

        text = Ext.create({
            xtype: "textarea",
            layout: 'fit',
            width: '100%',
            height: 700,
            scrollable: true,
            padding: 4
        });

        return Ext.create("Ext.panel.Panel", {
            items: [
                text
            ],
            showResult: function(result) {
                text.setValue(result);
            }
        });
    },

    getArgs: function() {
        var me = this;
        return {
            "script": "commands",
            "args": {
                "commands": [
                    // @todo: Split lines
                    me.commandsField.getValue().split("\n")
                ]
            }
        }
    }
});
