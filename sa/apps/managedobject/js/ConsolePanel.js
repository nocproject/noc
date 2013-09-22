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

        me.prompt = "&gt;&nbsp;";
        me.cmdHistory = [];
        me.cmdIndex = null;

        me.cmdField = Ext.create("Ext.form.field.Text", {
            width: 500,
            listeners: {
                scope: me,
                specialkey: me.onSpecialKey
            }
        });

        me.consoleBody = Ext.create("Ext.container.Container", {
            autoEl: {
                tag: "pre",
                cls: "noc-console"
            },
            autoScroll: true
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
                    items: [
                        ">",
                        me.cmdField
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
    preview: function(record) {
        var me = this;
        me.currentRecord = record;
        me.setTitle(record.get("name") + " console");
        me.clearBody();
        me.prompt = record.get("name") + "&gt;&nbsp;"
        me.cmdField.focus();
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
        me.consoleBody.update(
            v + "<div class='cmd'>" + me.prompt + Ext.htmlEncode(cmd) + "</div>"
        );
        me.scrollDown();
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
                me.consoleBody.update(
                    me.consoleBody.html + "<div class='result'>" +
                        Ext.htmlEncode(t) + "</div>");
                me.scrollDown();
                me.cmdField.focus();
            },
            failure: function() {
                NOC.error("Failed to run command");
            }
        });
    },
    //
    scrollDown: function() {
        var me = this;
        me.consoleBody.scrollBy(0, Infinity, true);
    },
    //
    clearBody: function() {
        var me = this;
        me.consoleBody.update("<div class='banner'>Welcome to the "
            + me.currentRecord.get("name") + " console!</div>");
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    }
});
