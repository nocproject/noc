//---------------------------------------------------------------------
// fm.event application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.Application");

Ext.define("NOC.fm.event.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.core.ModelStore",
    "NOC.core.JSONPreview",
    "NOC.sa.managedobject.LookupField",
    "NOC.inv.resourcegroup.Model",
    "NOC.sa.administrativedomain.LookupField",
    "NOC.fm.eventclass.LookupField",
    "NOC.fm.event.EventPanel",
    "NOC.core.combotree.ComboTree",
    "NOC.core.ComboBox",
    "NOC.fm.event.ApplicationModel",
    "NOC.fm.event.ApplicationController",
  ],
  layout: "card",
  controller: "fm.event",
  viewModel: {
    type: "fm.event",
  },
  STATUS_MAP: {
    A: "Active",
    S: "Archived",
    F: "Failed",
  },
  //
  initComponent: function(){
    var me = this,
      bs = Math.max(50, Math.ceil(screen.height / 24) + 10);

    me.currentQuery = {status: "A"};
    me.store = Ext.create("NOC.core.ModelStore", {
      model: "NOC.fm.event.Model",
      autoLoad: false,
      customFields: [],
      pageSize: bs,
      leadingBufferZone: bs,
      numFromEdge: bs,
      trailingBufferZone: bs,
      sorters: [
        {
          property: "timestamp",
          direction: "DESC",
        },
      ],
    });

    me.gridPanel = Ext.create("Ext.grid.Panel", {
      region: "center",
      split: true,
      store: me.store,
      border: false,
      itemId: "fm-event-grid",
      stateful: true,
      stateId: "fm.event-grid",
      columns: [
        {
          text: __("ID"),
          dataIndex: "id",
          width: 150,
        },
        {
          text: __("Status"),
          dataIndex: "status",
          width: 50,
          renderer: NOC.render.Choices(me.STATUS_MAP),
          hidden: true,
        },
        {
          text: __("Time"),
          dataIndex: "timestamp",
          width: 100,
          renderer: NOC.render.DateTime,
        },
        {
          text: __("Administrative Domain"),
          dataIndex: "administrative_domain",
          width: 200,
          renderer: NOC.render.Lookup("administrative_domain"),
        },
        {
          text: __("Object"),
          dataIndex: "managed_object",
          width: 200,
          renderer: NOC.render.Lookup("managed_object"),
        },
        {
          text: __("Class"),
          dataIndex: "event_class",
          width: 300,
          renderer: NOC.render.Lookup("event_class"),
        },
        {
          text: __("Subject"),
          dataIndex: "subject",
          flex: 1,
        },
        {
          text: __("Alrm."),
          dataIndex: "alarms",
          width: 30,
          align: "right",
        },
        {
          text: __("Rep."),
          dataIndex: "repeats",
          width: 30,
          align: "right",
        },
        {
          text: __("Dur."),
          dataIndex: "duration",
          width: 70,
          align: "right",
          renderer: NOC.render.Duration,
        },
      ],
      selModel: {
        selType: "checkboxmodel",
      },
      viewConfig: {
        enableTextSelection: true,
        getRowClass: Ext.bind(me.getRowClass, me),
      },
      listeners: {
        itemdblclick: {
          scope: me,
          fn: me.onSelectEvent,
        },
      },
    });

    me.filterPanel = Ext.create("Ext.form.Panel", {
      region: "east",
      width: 210,
      split: true,
      titleAlign: "right",
      minWidth: 210,
      title: __("Filters"),
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
          title: __("Control"),
          width: "100%",
          items: [
            {
              xtype: "fieldcontainer",
              padding: "5 0 5",
              layout: "column",
              defaults: {
                xtype: "button",
                width: "50%",
              },
              items: [
                {
                  itemId: "reload-button",
                  text: __("Reload"),
                  iconAlign: "right",
                  enableToggle: true,
                  tooltip: __("Toggle auto reload"),
                  pressed: false,
                  glyph: NOC.glyph.ban, // or "NOC.glyph.refresh" when pressed is true
                  listeners: {
                    toggle: "onAutoReloadToggle",
                  },
                },
                {
                  text: __("Reset Filter"),
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

    me.mainPanel = Ext.create("Ext.panel.Panel", {
      layout: "border",
      itemId: "fm-event-main",
      items: [
        me.gridPanel,
        me.filterPanel,
      ],
    });
    //
    me.eventPanel = Ext.create("NOC.fm.event.EventPanel", {
      app: me,
    });
    //
    me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
      app: me,
      restUrl: new Ext.XTemplate("/fm/event/{id}/json/"),
      previewName: new Ext.XTemplate("Event: {id}"),
    });
    me.ITEM_GRID = me.registerItem(me.mainPanel);
    me.ITEM_FORM = me.registerItem(me.eventPanel);
    me.ITEM_JSON = me.registerItem(me.jsonPanel);
    Ext.apply(me, {
      items: me.getRegisteredItems(),
    });
    me.callParent();
    //
    if(me.getCmd() === "history"){
      me.showEvent(me.noc.cmd.args[0]);
    }

  },
  // Return Grid's row classes
  getRowClass: function(record){
    var c = record.get("row_class");
    if(c){
      return c;
    } else{
      return "";
    }
  },
  //
  showGrid: function(){
    var me = this;
    me.getLayout().setActiveItem(0);
    if(me.down("[itemId=reload-button]").pressed){
      me.getController().startPolling();
    }
    me.setHistoryHash();
  },
  //
  onSelectEvent: function(grid, record){
    var me = this;
    me.getController().stopPolling();
    me.getLayout().setActiveItem(1);
    me.eventPanel.showEvent(record.get("id"));
  },
  //
  showForm: function(){
    var me = this;
    me.showItem(me.ITEM_FORM);
  },
  //
  showEvent: function(id){
    var me = this,
      panel = me.showItem(me.ITEM_FORM);
    panel.showEvent(id);
  },
  //
  onCloseApp: function(){
    var me = this;
    me.getController().stopPolling();
  },
});
