//---------------------------------------------------------------------
// fm.alarmgroup application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmgroup.Application");

Ext.define("NOC.fm.alarmgroup.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.fm.alarmgroup.Model",
        "NOC.fm.alarmclass.LookupField"
    ],
    model: "NOC.fm.alarmgroup.Model",
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 100,
            align: "right"
        },
        {
            text: __("Active"),
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50,
            align: "right"
        },
        {
            text: __("Preference"),
            dataIndex: "preference",
            width: 50,
            align: "right"
        },
        {
            text: __("Alarm Class"),
            dataIndex: "alarm_class",
            renderer: NOC.render.Lookup("alarm_class"),
            width: 200
        },
        {
            text: __("ReferencePrefix"),
            dataIndex: "reference_prefix",
            width: 100,
            align: "right"
        },
        {
          text: __("Labels"),
          dataIndex: "labels",
          renderer: NOC.render.LabelField,
          width: 100
        }
    ],
    fields: [
        {
            name: 'name',
            xtype: 'textfield',
            fieldLabel: __('Name'),
            allowBlank: false,
            uiStyle: 'large'
        },
        {
            name: 'description',
            xtype: 'textarea',
            fieldLabel: __('Description'),
            uiStyle: 'extra'
        },
        {
            name: "preference",
            xtype: "numberfield",
            fieldLabel: __("Preference"),
            allowBlank: true,
            defaultValue: 999,
            minValue: 0
        },
        {
            name: "alarm_class",
            xtype: "fm.alarmclass.LookupField",
            fieldLabel: __("Alarm Class"),
            allowBlank: false
        },
        {
            name: 'reference_prefix',
            xtype: 'textarea',
            fieldLabel: __('Reference Prefix'),
            uiStyle: 'extra'
        },
        {
            name: 'title_template',
            xtype: 'textarea',
            fieldLabel: __('Title Template'),
            uiStyle: 'extra'
        },
        {
            name: "labels",
            xtype: "labelfield",
            fieldLabel: __("Match Labels"),
            allowBlank: false,
            isTree: true,
            pickerPosition: "down",
            uiStyle: "extra",
            query: {
                "allow_matched": true
            }
        }
    ]
});
