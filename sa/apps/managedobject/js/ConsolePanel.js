//---------------------------------------------------------------------
// sa.managed_object ConsolePanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.ConsolePanel");

Ext.define("NOC.sa.managedobject.ConsolePanel", {
    extend: "Ext.panel.Panel",
    app: null,
    layout: "fit",
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.prompt = "> ";
        me.cmdHistory = [];
        me.cmdIndex = null;

        me.cmdField = Ext.create("Ext.form.field.Text", {
            anchor: "100%",
            fieldLabel: ">",
            labelWidth: 16,
            itemId: "cmdfield",
            listeners: {
                scope: me,
                specialkey: me.onSpecialKey
            }
        });

        me.consoleBody = Ext.create("NOC.core.CMText", {
            readOnly: true
        });

        me.closeButton = Ext.create("Ext.button.Button", {
            text: "Close",
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose
        });

        me.clearButton = Ext.create("Ext.button.Button", {
            text: "Clear",
            glyph: NOC.glyph.eraser,
            scope: me,
            handler: me.clearBody
        });

        Ext.apply(me, {
            items: [
                me.consoleBody
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.closeButton,
                        "-",
                        me.clearButton
                    ]
                },
                {
                    xtype: "toolbar",
                    dock: "bottom",
                    layout: "fit",
                    items: [
                        me.cmdField
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
    preview: function(record) {
        var me = this,
            c = [record.get("name"), "console"],
            platform = record.get("platform");
        if(platform) {
            c.push("(" + platform + ")");
        }
        me.currentRecord = record;
        me.setTitle(c.join(" "));
        me.clearBody();
        me.prompt = record.get("name") + "> ";
    },
    //
    onSpecialKey: function(field, e) {
        var me = this;
        switch(e.getKey()) {
            case e.ENTER:
                me.submitCommand(field.getValue());
                field.setValue("");
                break;
            case e.ESC:
                field.setValue("");
                break;
            case e.UP:
                if(me.cmdIndex !== null) {
                    me.cmdIndex = Math.max(0, me.cmdIndex - 1);
                    field.setValue(me.cmdHistory[me.cmdIndex]);
                }
                break;
            case e.DOWN:
                if(me.cmdIndex !== null) {
                    me.cmdIndex = Math.min(
                        me.cmdIndex + 1,
                        me.cmdHistory.length - 1);
                    field.setValue(me.cmdHistory[me.cmdIndex]);
                }
                break;
        }
    },
    //
    submitCommand: function(cmd) {
        var me = this,
            v = me.consoleBody.html || "";

        // Maintain history
        if(me.cmdHistory.length === 0 || me.cmdHistory[me.cmdHistory.length - 1] != cmd) {
            me.cmdHistory.push(cmd);
        }
        me.cmdIndex = me.cmdHistory.length;
        // Display
        me.consoleOut(me.prompt + cmd);
        NOC.mrt({
            url: "/sa/managedobject/mrt/console/",
            selector: me.currentRecord.get("id"),
            mapParams: {
                commands: [cmd],
                ignore_cli_errors: true
            },
            loadMask: me,
            scope: me,
            success: function(result) {
                var t = "Timed out.";
                if(result) {
                    t = result[0].result[0];
                }
                me.consoleOut(t);
            },
            failure: function() {
                NOC.error("Failed to run command");
            }
        });
    },
    //
    clearBody: function() {
        var me = this;
        me.consoleBody.setValue("Welcome to the " + me.currentRecord.get("name") + " console!\n");
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    },

    consoleOut: function(v) {
        var me = this;
        me.consoleBody.setValue(
            me.consoleBody.getValue() + v + "\n"
        );
        me.consoleBody.scrollDown();
    },

    getDefaultFocus: function() {
        var me = this;
        return me.cmdField;
    }
});
