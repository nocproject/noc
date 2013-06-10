//---------------------------------------------------------------------
// pm.ts application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.ts.Application");

Ext.define("NOC.pm.ts.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.pm.pmts.Model",
        "NOC.pm.storage.LookupField",
        "NOC.pm.check.LookupField"
    ],
    model: "NOC.pm.ts.Model",
    idField: "ts_id",
    columns: [
        {
            text: "Check",
            dataIndex: "check",
            renderer: NOC.render.Lookup("check"),
            width: 200
        },
        {
            text: "Name",
            dataIndex: "name",
            width: 150
        },
        {
            text: "Storage",
            dataIndex: "storage",
            renderer: NOC.render.Lookup("storage"),
            flex: 1
        }
    ],
    fields: [
        {
            name: "check",
            fieldLabel: "Check",
            xtype: "pm.check.LookupField"
        },
        {
            name: "name",
            fieldLabel: "Name",
            xtype: "textfield"
        },
        {
            name: "storage",
            fieldLabel: "Storage",
            xtype: "pm.storage.LookupField"
        }
    ],
    //
    onPreview: function(record) {
        var me = this;
        Ext.create("NOC.pm.ts.GraphPreview", {
            title: Ext.String.format("{0} {1}", record.get("check__label"), record.get("name")),
            app: me,
            ts: record.get(me.idField)
        });
    }
});
