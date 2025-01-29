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
    type: "fm.alarm.container",
  },
  requires: [
    "NOC.fm.alarm.view.grids.ContainerModel",
    "NOC.fm.alarm.view.grids.ContainerController",
    "NOC.fm.alarm.view.grids.Active",
    "NOC.fm.alarm.view.grids.Recent",
    "NOC.fm.alarm.view.grids.Sidebar",
  ],
  layout: "border",
  reference: "fm-alarm-list",
  tbar: [
    {
      glyph: NOC.glyph.refresh,
      handler: "onRefresh",
    },
    {
      text: __("Filtering List"),
      glyph: NOC.glyph.filter,
      tooltip: __("Show/Hide Filter"),
      style: {
        pointerEvents: "all",
      },
      handler: "collapseFilter",
    },
    {
      glyph: NOC.glyph.download,
      text: __("Group actions"),
      tooltip: __("Group actions"),
      itemId: "alarm_action_menu",
      bind: {
        disabled: "{isActiveAlarmsSelected}",
      },
      menu: {
        xtype: "menu",
        plain: true,
        items: [
          {
            text: __("Group comment"),
            listeners: {
              click: "addGroupComment",
            },
          },
          {
            text: __("Escalate"),
            listeners: {
              click: "addGroupEscalate",
            },
          },
          {
            text: __("New Maintaince"),
            listeners: {
              click: "createMaintenance",
            },
          },
          {
            text: __("Alarm Detail Report"),
            listeners: {
              click: "openAlarmDetailReport",
            },
          },
          {
            text: __("Mark to favorites"),
            listeners: {
              click: "onGroupMarkFavorites",
            },
          },
          {
            text: __("Unmark from favorites"),
            listeners: {
              click: "onGroupUnmarkFavorites",
            },
          },
          {
            text: __("Clear alarms"),
            bind: {
              disabled: "{activeFilterIsClosed}",
            },
            listeners: {
              click: "onClearAlarms",
            },
          },
        ],
      },
    }],
  items: [
    {
      layout: "border",
      region: "center",
      bind: {
        disabled: "{containerDisabled}",
      },
      items: [
        {
          xtype: "fm.alarm.recent",
          reference: "fm-alarm-recent",
          region: "north",
          height: "25%",
          hidden: true,
          split: true,
          listeners: {
            fmAlarmReload: "onReload",
          },
        },
        {
          xtype: "fm.grid.active",
          reference: "fm-alarm-active",
          region: "center",
          listeners: {
            fmAlarmReload: "onReload",
            fmAlarmLoaded: "onStoreLoaded",
            fmAlarmSelectionChange: "onStoreSelectionChange",
            itemdblclick: "onSelectAlarm",
          },
        },
      ],
    },
    {
      xtype: "fm.alarm.sidebar",
      reference: "fm-alarm-sidebar",
      region: "east",
      width: "20%",
      split: true,
      collapsed: true,
      hideCollapseTool: true,
      border: false,
      animCollapse: false,
      collapseMode: "mini",
      listeners: {
        fmAlarmSidebarResetSelection: "onActiveResetSelection",
      },
    },
  ],
});
