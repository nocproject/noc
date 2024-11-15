//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.Sidebar");

Ext.define("NOC.fm.alarm.view.grids.Sidebar", {
  extend: "Ext.form.Panel",
  alias: "widget.fm.alarm.sidebar",
  controller: "fm.alarm.sidebar",
  viewModel: {
    type: "fm.alarm.sidebar",
  },
  requires: [
    "NOC.core.combotree.ComboTree",
    "NOC.core.ComboBox",
    "NOC.core.tagfield.Tagfield",
    "NOC.fm.alarm.view.grids.SidebarModel",
    "NOC.fm.alarm.view.grids.SidebarController",
    "NOC.fm.alarm.view.grids.ProfileFilter",
    "NOC.fm.alarm.view.grids.DisplayFilter",
    "Ext.ux.form.SearchField",
  ],
  reference: "fm-alarm-filter",
  bind: {
    title: "{alarmsTotal}",
  },
  titleAlign: "right",
  minWidth: 350,
  scrollable: {
    indicators: false,
    x: false,
    y: true,
  },
  suspendLayout: true,
  defaults: {
    xtype: "fieldset",
    margin: 5,
    collapsible: true,
  },
  items: [
    {
      title: __("Summary"),
      bind: {hidden: "{isActiveAlarmsSelected}"},

      items: [
        {
          layout: "column",
          border: false,
          items: [
            {xtype: "displayfield", columnWidth: 1, bind: {value: "{summaryTotal}"} },
            {xtype: "displayfield", width: 30, bind: {value: "{total.objects}"} },
            {xtype: "displayfield", columnWidth: 1, bind: {value: "{summaryFiltered}"} },
            {xtype: "displayfield", width: 30, bind: {value: "{total.objectsFiltered}"} },
          ],
        },
        {xtype: "button", text: __("Reset"), width: 50, margin: "0 0 5 0", handler: "onResetStatuses"},
      ],
    },
    {
      title: __("Control"),
      detaults: {
        xtype: "checkboxfield",
      },
      items: [
        {
          xtype: "fieldcontainer",
          layout: "column",
          padding: "5 0 5",
          defaults: {
            xtype: "button",
            columnWidth: .33,
            enableToggle: true,
          },
          items: [
            {
              text: __("Reload"),
              iconAlign: "right",
              enableToggle: true,
              tooltip: __("Toggle autoreload"),
              bind: {
                glyph: "{autoReloadIcon}",
                pressed: "{autoReload}",
              },
              listeners: {
                toggle: "onAutoReloadToggle",
              },
            },
            {
              tooltip: __("Toggle sound"),
              bind: {
                glyph: "{volumeIcon}",
                pressed: "{volume}",
              },
              listeners: {
                toggle: "onSoundToggle",
              },
            },
            {
              text: __("Reset Filter"),
              iconAlign: "right",
              enableToggle: false,
              listeners: {
                click: "onResetFilter",
              },
            },
          ],
        },
      ],
    },
    {
      title: __("Alarms type"),
      collapsed: false,
      defaults: {
        xtype: "radiogroup",
        columns: 2,
      },
      items: [
        {
          name: "status",
          bind: {value: "{status}"},
          items: [
            {
              boxLabel: __("Active"),
              inputValue: "A",
              // ToDo make all tooltip
              // tooltip: __("Show active alarms"),
            },
            {
              boxLabel: __("Closed"),
              inputValue: "C",
              // tooltip: __("Show archived alarms")
            },
          ],
        },
        {
          xtype: "fieldcontainer",
          layout: "column",
          defaults: {
            xtype: "radiogroup",
            columns: 2,
            labelAlign: "top",
            columnWidth: .5,
          },
          items: [
            {
              fieldLabel: __("Root"),
              name: "collapse",
              bind: {value: "{collapse}"},
              items: [
                {
                  boxLabel: __("Only"),
                  inputValue: 1,
                  // tooltip: __("Show only root causes"),
                },
                {
                  boxLabel: __("All"),
                  inputValue: 0,
                  // tooltip: __("Show all alarms")
                },
              ],
            },
            {
              name: "wait_tt",
              bind: {value: "{wait_tt}"},
              fieldLabel: "TT",
              items: [
                {
                  boxLabel: __("Wait"),
                  inputValue: 1,
                  // tooltip: __("Show only waiting confirmation"),
                },
                {
                  boxLabel: __("All"),
                  inputValue: 0,
                  // tooltip: __("Show all alarms")
                },
              ],
            },
          ],
        },
        {
          fieldLabel: __("Maintenance"),
          name: "maintenance",
          bind: {value: "{maintenance}"},
          labelAlign: "top",
          columns: 3,
          items: [
            {
              boxLabel: __("Hide"),
              // tooltip: __("Hide alarms covered by maintenance"),
              inputValue: "hide",
            },
            {
              boxLabel: __("Only"),
              // tooltip: __("Show only alarms covered by maintenance"),
              inputValue: "only",
            },
            {
              boxLabel: __("All"),
              // tooltip: __("Show all alarms"),
              inputValue: "show",
            },
          ],
        },
        {
          xtype: "fieldcontainer",
          layout: "column",
          defaults: {
            xtype: "radiogroup",
            columns: 2,
            labelAlign: "top",
            columnWidth: .5,
          },
          items: [
            {
              fieldLabel: __("Alarm Group"),
              name: "alarm_group",
              bind: {value: "{alarm_group}"},
              items: [
                {
                  boxLabel: __("Only"),
                  inputValue: "only",
                  // tooltip: __("Show only alarm causes"),
                },
                {
                  boxLabel: __("All"),
                  inputValue: "show",
                  // tooltip: __("Show all alarms")
                },
              ],
            },
            {
              name: "ephemeral",
              bind: {value: "{ephemeral}"},
              fieldLabel: "Ephemeral",
              items: [
                {
                  boxLabel: __("Show"),
                  inputValue: 1,
                  // tooltip: __("Show only waiting confirmation"),
                },
                {
                  boxLabel: __("Hide"),
                  inputValue: 0,
                  // tooltip: __("Show all alarms")
                },
              ],
            },
          ],
        },
      ],
    },
    {
      title: __("Filters"),
      collapsed: false,
      defaults: {
        labelAlign: "top",
        width: "100%",
      },
      items: [
        {
          xtype: "core.combo",
          restUrl: "/sa/managedobject/lookup/",
          fieldLabel: __("Object"),
          name: "managed_object",
          bind: {
            selection: "{activeFilter.managed_object}",
          },
        },
        {
          xtype: "noc.core.combotree",
          restUrl: "/inv/networksegment/",
          fieldLabel: __("Segment"),
          name: "segment",
          bind: {
            selection: "{activeFilter.segment}",
          },
        },
        {
          xtype: "core.tagfield",
          url: "/sa/administrativedomain/lookup/",
          lazyLoadTree: true,
          fieldLabel: __("Adm. Domain"),
          name: "administrative_domain",
          bind: {
            selected: "{activeFilter.administrative_domain}",
          },
        },
        {
          name: "resource_group",
          xtype: "noc.core.combotree",
          restUrl: "/inv/resourcegroup/",
          fieldLabel: __("By Resource Group (Selector)"),
          listWidth: 1,
          listAlign: "left",
          labelAlign: "top",
          allowBlank: true,
          bind: {
            selection: "{activeFilter.resource_group}",
          },
        },
        {
          xtype: "core.tagfield",
          url: "/fm/alarmclass/lookup/",
          fieldLabel: __("Class"),
          name: "alarm_class",
          bind: {
            selected: "{activeFilter.alarm_class}",
          },
        },
        {
          xtype: "searchfield",
          fieldLabel: __("TT"),
          name: "escalation_tt__contains",
          triggers: {
            clear: {
              cls: "x-form-clear-trigger",
              hidden: true,
              handler: function(field){
                field.setValue(null);
                field.fireEvent("select", field);
              },
            },
          },
          listeners: {
            change: function(field, value){
              if(value == null || value === ""){
                this.getTrigger("clear").hide();
                return;
              }
              this.getTrigger("clear").show();
            },
          },
          bind: {value: "{activeFilter.escalation_tt__contains}"},
        },
        {
          xtype: "fieldcontainer",
          fieldLabel: __("By Date"),
          layout: "column",
          padding: "5 0 5",
          defaults: {
            xtype: "datefield",
            format: "d.m.Y",
            submitFormat: "Y-m-d\\TH:i:s",
            startDay: 1,
            width: "50%",
            hideLabel: true,
          },
          items: [ // format 2018-11-16T00:00:00
            {
              name: "timestamp__gte",
              bind: {value: "{activeFilter.timestamp__gte}"},
            },
            {
              name: "timestamp__lte",
              bind: {value: "{activeFilter.timestamp__lte}"},
            },
          ],
        },
        {
          xtype: "fm.alarm.filter.profile",
          name: "profile",
          fieldLabel: __("Service Profiles"),
          bind: {value: "{activeFilter.profiles}"},
        },
      ],
    },
    {
      title: __("Display filters"),
      collapsed: false,
      reference: "fm-alarm-display-filters",
      items: [
        {
          xtype: "fm.alarm.display",
        },
      ],
    },
    {
      title: __("Show recently closed"),
      collapsed: true,
      reference: "fm-alarm-recent-switcher",
      items: [
        {
          xtype: "combo",
          queryMode: "local",
          valueField: "value",
          bind: {value: "{recentFilter.cleared_after}"},
          width: "100%",
          editable: false,
          store: {
            fields: ["value", "text"],
            data: [
              {"value": 0, "text": __("don't show")},
              {"value": 300, "text": __("5 min")},
              {"value": 900, "text": __("15 min")},
              {"value": 1800, "text": __("30 min")},
              {"value": 3600, "text": __("60 min")},
              {"value": 10800, "text": __("3 h")},
            ],
          },
        },
      ],
    },
  ],
  initComponent: function(){
    var addListeter = function(field){
      field.getPicker().on({
        beforeshow: this.onBeforePickerShow,
      })
    };
    this.callParent();
    this.enableBubble("fmAlarmResetFilter");
    Ext.each(this.query("[xtype=datefield]"), addListeter, this);
  },
  onBeforePickerShow: function(picker){
    picker.setPosition(picker.getRefOwner().getPosition());
  },
});
