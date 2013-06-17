//---------------------------------------------------------------------
// TCPCheckForm
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.check.tcp.TCPCheckForm");

Ext.define("NOC.pm.check.tcp.TCPCheckForm", {
    extend: "Ext.form.Panel",
    items: [
        {
            name: "address",
            fieldLabel: "Address",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "port",
            fieldLabel: "Port",
            xtype: "numberfield",
            allowBlank: false
        },
        {
            name: "timeout",
            fieldLabel: "Timeout",
            xtype: "numberfield",
            allowBlank: false
        },
        {
            name: "request",
            fieldLabel: "Request",
            xtype: "textarea",
            allowBlank: true
        },
        {
            name: "response",
            fieldLabel: "Response",
            xtype: "textfield",
            allowBlank: true
        },
        {
            name: "wait_close",
            boxLabel: "Wait Until Socket Close",
            xtype: "checkboxfield"
        }
    ]
});
