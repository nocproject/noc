//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.form.Alarm");

Ext.define("NOC.fm.alarm.view.form.Alarm", {
  extend: "Ext.panel.Panel",
  alias: "widget.fm.alarm.form",
  controller: "fm.alarm.form",
  viewModel: {
    type: "fm.alarm.form",
  },
  requires: [
    "NOC.fm.alarm.view.form.AlarmModel",
    "NOC.fm.alarm.view.form.AlarmController",
  ],
  layout: "border",
  reference: "fm-alarm-form",
  items: [
    {
      xtype: "panel",
      region: "north",
      resizable: true,
      layout: "fit",
      hideCollapseTool: true,
      hideHeaders: true,
      split: true,
      items: [
        {
          xtype: "displayfield",
          bind: {
            value: "{header}",
          },
        },
      ],
    },
    {
      xtype: "tabpanel",
      reference: "fm-alarm-form-tab-panel",
      region: "center",
      items: [
        {
          xtype: "container",
          title: __("Overview"),
          scrollable: true,
          bind: {
            html: "{overviewPanel}",
          },
        },
        {
          xtype: "container",
          title: __("Help"),
          scrollable: true,
          bind: {
            html: "{helpPanel}",
            disabled: "{!selected.symptoms}",
          },
        },
        {
          xtype: "container",
          title: __("Data"),
          scrollable: true,
          bind: {
            html: "{dataPanel}",
            disabled: "{!hasVars}",
          },
        },
        {
          xtype: "grid",
          reference: "fm-alarm-log",
          title: __("Log"),
          scrollable: true,
          bind: {
            store: "{selectedLog}",
          },
          columns: [
            {
              dataIndex: "timestamp",
              text: __("Time"),
              renderer: NOC.render.DateTime,
              width: 120,
            },
            {
              dataIndex: "from_status",
              text: __("From"),
              renderer: "onRenderStatus",
              width: 50,
            },
            {
              dataIndex: "to_status",
              text: __("To"),
              renderer: "onRenderStatus",
              width: 50,
            },
            {
              dataIndex: "message",
              text: __("Message"),
              flex: 1,
            },
          ],
          dockedItems: [
            {
              xtype: "toolbar",
              dock: "bottom",
              items: [
                {
                  xtype: "textfield",
                  fieldLabel: __("New message"),
                  labelStyle: "white-space: nowrap;",
                  labelPad: 10,
                  fieldStyle: "margin: 0 4px;",
                  labelAlign: "right",
                  width: "100%",
                  listeners: {
                    specialkey: {
                      fn: "onMessageKey",
                    },
                  },
                },
              ],
            },
          ],
        },
        {
          xtype: "grid",
          reference: "fm-alarm-events",
          title: __("Events"),
          scrollable: true,
          bind: {
            store: "{selectedEvents}",
          },
          columns: [
            {
              dataIndex: "id",
              text: __("ID"),
              width: 150,
            },
            {
              dataIndex: "timestamp",
              text: __("Time"),
              renderer: NOC.render.DateTime,
              width: 120,
            },
            {
              dataIndex: "event_class",
              text: __("Class"),
              renderer: NOC.render.Lookup("event_class"),
              width: 200,
            },
            {
              dataIndex: "subject",
              text: __("Subject"),
              flex: 1,
            },
          ],
        },
        {
          xtype: "treepanel",
          title: __("Alarms"),
          bind: {
            store: "{selectedAlarms}",
            disabled: "{!hasAlarms}",
          },
          rootVisible: false,
          useArrows: true,
          columns: [
            {
              xtype: "treecolumn",
              dataIndex: "id",
              text: __("ID"),
              width: 200,
            },
            {
              dataIndex: "timestamp",
              text: __("Time"),
              width: 120,
              renderer: NOC.render.DateTime,
            },
            {
              dataIndex: "managed_object",
              text: __("Managed Object"),
              width: 200,
              renderer: NOC.render.Lookup("managed_object"),
            },
            {
              dataIndex: "alarm_class",
              text: __("Class"),
              renderer: NOC.render.Lookup("alarm_class"),
            },
            {
              dataIndex: "subject",
              text: __("Subject"),
              flex: 1,
            },
          ],
          listeners: {
            itemdblclick: "onRowDblClickTreePanel",
          },
          viewConfig: {
            getRowClass: function(record){
              var c = record.get("row_class");
              return c ? c : "";
            },
          },
        },
        {
          xtype: "grid",
          reference: "fm-alarm-groups",
          title: __("Groups"),
          scrollable: true,
          bind: {
            store: "{selectedGroups}",
          },
          columns: [
            {
              dataIndex: "id",
              text: __("ID"),
              width: 150,
            },
            {
              dataIndex: "timestamp",
              text: __("Time"),
              renderer: NOC.render.DateTime,
              width: 120,
            },
            {
              dataIndex: "alarm_class",
              text: __("Class"),
              renderer: NOC.render.Lookup("alarm_class"),
              width: 200,
            },
            {
              dataIndex: "subject",
              text: __("Subject"),
              flex: 1,
            },
          ],
        },
      ],
    },
  ],
  tbar: [
    {
      text: __("Close"),
      tooltip: __("Close without saving"),
      glyph: NOC.glyph.arrow_left,
      handler: "onClose",
    },
    {
      glyph: NOC.glyph.refresh,
      handler: "onRefreshForm",
    },
    "-",
    {
      text: __("Escalate"),
      glyph: NOC.glyph.ambulance,
      tooltip: __("Escalate"),
      bind: {
        disabled: "{isClosed}",
      },
      handler: "onEscalateObject",
    },
    {
      text: __("Card"),
      glyph: NOC.glyph.eye,
      handler: "onShowCard",
    },
    {
      itemId: "showMapBtn",
      xtype: "splitbutton",
      text: __("Show Map"),
      glyph: NOC.glyph.globe,
      menu: [ // Dynamically add items, in showMapHandler from Controller
      ],
    },
    {
      text: __("Show Object"),
      glyph: NOC.glyph.pencil,
      handler: "onShowObject",
    },
    "-",
    {
      text: __("Clear"),
      glyph: NOC.glyph.eraser,
      handler: "onClear",
      bind: {
        disabled: "{isNotActive}",
      },
    },
    {
      enableToggle: true,
      glyph: NOC.glyph.star,
      bind: {
        text: "{favoriteText}",
        pressed: "{isFavorite}",
        disabled: "{isNotActive}",
        iconCls: "{favIconCls}",
      },
      handler: "onAddRemoveFav",
    },
    {
      text: __("Watch"),
      enableToggle: true,
      bind: {
        pressed: "{isSubscribe}",
        disabled: "{isNotActive}",
      },
      glyph: NOC.glyph.eye,
      handler: "onWatch",
    },
    {
      text: __("Set Root"),
      glyph: NOC.glyph.paperclip,
      handler: "onSetRoot",
      bind: {
        disabled: "{isNotActive}",
      },
    },
    {
      enableToggle: true,
      bind: {
        pressed: "{isAcknowledge}",
        disabled: "{isAcknowledgeDisabled}",
        text: "{acknowledgeText}",
      },
      handler: "onAcknowledge",
    },
    "->",
    {
      xtype: "displayfield",
      fieldLabel: __("ID"),
      labelWidth: 20,
      labelClsExtra: "noc-label-required",
      bind: {
        value: "{selected.id}",
      },
    },
  ],
});
