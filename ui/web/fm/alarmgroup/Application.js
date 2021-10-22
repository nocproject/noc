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
            align: "left"
        },
        {
            text: __("Active"),
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 100,
            align: "left"
        },
        {
            text: __("Preference"),
            dataIndex: "preference",
            width: 100,
            align: "left"
        },
        {
            text: __("Alarm Class"),
            dataIndex: "alarm_class",
            renderer: NOC.render.Lookup("alarm_class"),
            width: 200
        },
        {
            text: __("Reference Prefix"),
            dataIndex: "reference_prefix",
            width: 150,
            align: "left"
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
            uiStyle: 'large'
        },
        {
            name: "preference",
            xtype: "numberfield",
            fieldLabel: __("Preference"),
            allowBlank: true,
            uiStyle: 'small',
            defaultValue: 999,
            minValue: 0
        },
        {
            name: "alarm_class",
            xtype: "fm.alarmclass.LookupField",
            fieldLabel: __("Alarm Class"),
            uiStyle: 'large',
            allowBlank: false
        },
        {
            name: 'reference_prefix',
            xtype: 'textfield',
            fieldLabel: __('Reference Prefix'),
            uiStyle: 'large'
        },
        {
            name: 'title_template',
            xtype: 'textarea',
            fieldLabel: __('Title Template'),
            uiStyle: 'large'
        },
        {
            name: "labels",
            xtype: "labelfield",
            fieldLabel: __("Match Labels"),
            allowBlank: true,
            isTree: true,
            pickerPosition: "down",
            uiStyle: "large",
            query: {
                "allow_matched": true
            }
        }
    ]
});
