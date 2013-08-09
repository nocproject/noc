//---------------------------------------------------------------------
// fm.classificationrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.classificationrule.Application");

Ext.define("NOC.fm.classificationrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.classificationrule.Model",
        "NOC.fm.eventclass.LookupField"
    ],
    model: "NOC.fm.classificationrule.Model",
    search: true,

    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 500
        },
        {
            text: "Builtin",
            dataIndex: "is_builtin",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Event Class",
            dataIndex: "event_class",
            flex: 1,
            renderer: NOC.render.Lookup("event_class")
        },
        {
            text: "Pref",
            dataIndex: "preference",
            width: 50
        }
    ],
    fields: [
        {
            xtype: "textfield",
            name: "name",
            fieldLabel: "Name",
            allowBlank: false
        },
        {
            xtype: "textarea",
            name: "description",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            xtype: "numberfield",
            name: "preference",
            fieldLabel: "Preference",
            allowBlank: false,
            defaultValue: 1000,
            minValue: 0,
            maxValue: 10000
        },
        {
            xtype: "fm.eventclass.LookupField",
            name: "event_class",
            fieldLabel: "Event Class",
            allowBlank: false
        }
    ]/*,
    filters: [
        {
            title: "Builtin",
            name: "is_builtin",
            ftype: "bool"
        }
        {
            title: "By Event Class",
            name: "event_class",
            ftype: "lookup",
            lookup: "fm.eventclass"
        }
    ]*/
});
