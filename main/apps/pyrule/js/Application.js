//---------------------------------------------------------------------
// main.pyrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pyrule.Application");

Ext.define("NOC.main.pyrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.pyrule.Model",
        "NOC.main.ref.interface.LookupField"
    ],
    model: "NOC.main.pyrule.Model",
    formLayout: {
        type: "vbox",
        align: "stretch"
    },
    search: true,
    initComponent: function () {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 200
                },

                {
                    text: "Interface",
                    dataIndex: "interface",
                    width: 200
                },
                {
                    text: "handler",
                    dataIndex: "handler",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false,
                    uiStyle: "medium",
                },
                {
                    name: "interface",
                    xtype: "main.ref.interface.LookupField",
                    fieldLabel: "Interface",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textareafield",
                    fieldLabel: "Description",
                    allowBlank: false,
                    uiStyle: "extra"
                },
                {
                    name: "handler",
                    xtype: "textfield",
                    fieldLabel: "Handler",
                    allowBlank: true,
                    uiStyle: "large",
                    triggers: {
                        clear: {
                            cls: Ext.baseCSSPrefix + "form-clear-trigger",
                            handler: function(field) {
                                field.reset();
                            }
                        }
                    }
                },
                {
                    name: "text",
                    xtype: "cmtext",
                    fieldLabel: "Text",
                    allowBlank: true,
                    flex: 1,
                    mode: "python"
                }
            ]
        });
        me.callParent();
    },
    showOpError: function (action, op, status) {
        var me = this;
        // Detect Syntax Errors
        if (status.traceback) {
            var rx = /^Syntax error: (.+) \(<string>, line (\d+)\)$/i,
                g = rx.exec(status.traceback);
            if (g != null) {
                var error = g[1],
                    line = g[2];
                NOC.error("Syntax error at line " + line + "<br/>" + error);
                return;
            }
        }
        me.callParent([action, op, status]);
    }
});
