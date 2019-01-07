//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.Container");

Ext.define("NOC.fm.alarm.view.grids.Container", {
    extend: "Ext.panel.Panel",
    alias: "widget.fm.alarm.container",
    controller: "fm.alarm.container",
    viewModel: {
        type: "fm.alarm.container"
    },
    requires: [
        "NOC.fm.alarm.view.grids.ContainerModel",
        "NOC.fm.alarm.view.grids.ContainerController",
        "NOC.fm.alarm.view.grids.Active",
        "NOC.fm.alarm.view.grids.Recent",
        "NOC.fm.alarm.view.grids.Sidebar"
    ],
    layout: 'border',
    reference: "fm-alarm-list",
    items: [
        {
            layout: "border",
            region: "center",
            items: [
                {
                    xtype: "fm.alarm.recent",
                    reference: "fm-alarm-recent",
                    region: "north",
                    height: "25%",
                    hidden: true,
                    split: true,
                    listeners: {
                        fmAlarmReload: "onReload"
                    }
                },
                {
                    xtype: "fm.grid.active",
                    reference: "fm-alarm-active",
                    region: "center",
                    listeners: {
                        fmAlarmReload: "onReload",
                        fmAlarmLoaded: "onStoreLoaded",
                        fmAlarmSelectionChange: "onStoreSelectionChange",
                        itemdblclick: "onSelectAlarm"
                    }
                }
            ]
        },
        {
            xtype: "fm.alarm.sidebar",
            reference: "fm-alarm-sidebar",
            region: "east",
            width: "20%",
            split: true
        }
    ]
});