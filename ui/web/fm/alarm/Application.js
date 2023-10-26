//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.Application");

Ext.define("NOC.fm.alarm.Application", {
    extend: "NOC.core.Application",
    layout: "card",
    itemId: "fmAlarm",
    controller: "fm.alarm",
    viewModel: {
        type: "fm.alarm"
    },
    requires: [
        "Ext.layout.container.Card",
        "NOC.fm.alarm.view.form.Alarm",
        "NOC.fm.alarm.view.grids.Container",
        "NOC.fm.alarm.ApplicationModel",
        "NOC.fm.alarm.ApplicationController"
    ],
    reference: "fmAlarm",
    bind: {
        activeItem: "{activeItem}"
    },
    items: [
        {
            itemId: "fmAlarmList",
            xtype: "fm.alarm.container",
            listeners: {
                fmAlarmSelectItem: "onOpenForm",
                fmAlarmResetFilter: "onResetFilter"
            }
        },
        {
            itemId: "fmAlarmForm",
            xtype: "fm.alarm.form",
            listeners: {
                fmAlarmCloseForm: "onCloseForm",
                fmAlarmRefreshForm: "onRefreshForm",
                fmAlarmSelectItem: "onOpenForm"
            }
        }
    ]
});
