//---------------------------------------------------------------------
// fm.event application filter panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.EventFilter");

Ext.define("NOC.fm.event.EventFilter", {
  extend: "Ext.form.Panel",
  border: false,
  minWidth: 210,
  title: __("Filter"),
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
      xtype: "button",
      text: __("Reset Filter"),
      enableToggle: false,
      listeners: {
        click: "onResetFilter",
      },
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
          xtype: "combo",
          fieldLabel: __("State"),
          editable: false,
          queryMode: "local",
          displayField: "name",
          valueField: "id",
          store: {
            fields: ["id", "name"],
            data: [
              {id: "A", name: "Active"},
              {id: "S", name: "Archived"},
              {id: "F", name: "Failed"},
            ],
          },
          name: "status",
          bind: {
            value: "{filter.status}",
          },
        },
        {
          xtype: "core.combo",
          restUrl: "/sa/managedobject/lookup/",
          fieldLabel: __("Object"),
          name: "managed_object",
          bind: {
            selection: "{filter.managed_object}",
          },
        },
        {
          xtype: "noc.core.combotree",
          restUrl: "/sa/administrativedomain/",
          fieldLabel: __("Adm. Domain"),
          name: "administrative_domain",
          bind: {
            selection: "{filter.administrative_domain}",
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
            selection: "{filter.resource_group}",
          },
        },
        {
          xtype: "core.combo",
          restUrl: "/fm/eventclass/lookup/",
          fieldLabel: __("Event Class"),
          name: "event_class",
          bind: {
            selection: "{filter.event_class}",
          },
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
              bind: {value: "{filter.timestamp__gte}"},
            },
            {
              name: "timestamp__lte",
              bind: {value: "{filter.timestamp__lte}"},
            },
          ],
        },
      ],
    },
  ],
});