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
        "NOC.fm.alarm.view.form.Basket",
        "NOC.fm.alarm.view.grids.ContainerModel",
        "NOC.fm.alarm.view.grids.ContainerController",
        "NOC.fm.alarm.view.grids.Active",
        "NOC.fm.alarm.view.grids.Recent",
        "NOC.fm.alarm.view.sidebar.Sidebar"
    ],
    layout: 'border',
    reference: "fmAlarmList",
    tbar: [
        {
            glyph: NOC.glyph.download,
            text: __("Group actions"),
            tooltip: __("Group actions"),
            itemId: "alarm_action_menu",
            bind: {
                disabled: "{isActiveAlarmsSelected}"
            },
            menu: {
                xtype: "menu",
                plain: true,
                items: [
                    {
                        text: __("Group comment"),
                        listeners: {
                            click: "addGroupComment"
                        }
                    },
                    {
                        text: __("Escalate"),
                        listeners: {
                            click: "addGroupEscalate"
                        }
                    },
                    {
                        text: __("New Maintaince"),
                        listeners: {
                            click: "createMaintenance"
                        },
                    },
                    {
                        text: __("Alarm Detail Report"),
                        listeners: {
                            click: "openAlarmDetailReport"
                        },
                    }
                ]
            }
        }],
    items: [
        {
            reference: "fmAlarmListContainer",
            layout: "border",
            region: "center",
            items: [
                {
                    xtype: "fm.alarm.recent",
                    reference: "fmAlarmRecent",
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
                    reference: "fmAlarmActive",
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
            reference: "fmAlarmBasket",
            region: "center",
            xtype: "fm.alarm.basket",
            hidden: true,
            listeners: {
                fmAlarmBasketClose: "onBasketClose",
            }
        },
        {
            xtype: "fm.alarm.sidebar",
            reference: "fmAlarmSidebar",
            region: "east",
            width: "20%",
            split: true,
            listeners: {
                fmAlarmSidebarResetSelection: "onActiveResetSelection",
                fmAlarmSidebarUpdateBasket: "onUpdateBasket",
                fmAlarmSidebarUpdateOpenBasket: "onUpdateOpenBasket",
                fmAlarmSidebarNewBasket: "onNewBasket"
            }
        }
    ]
});
