//---------------------------------------------------------------------
// sa.managedobject SensorsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.SensorsPanel");

Ext.define("NOC.sa.managedobject.SensorsPanel", {
  extend: "NOC.core.ApplicationPanel",
  alias: "widget.sa.sensors",
  requires: [
    "NOC.core.ComboBox",
    "NOC.sa.managedobject.SensorsStore",
    "NOC.core.label.LabelField",
  ],
  app: null,
  autoScroll: true,
  historyHashPrefix: "sensors",
  rowClassField: "row_class",

  initComponent: function(){
    var me = this;
    me.gridPlugins = [];
    me.currentObject = null;

    me.refreshButton = Ext.create("Ext.button.Button", {
      text: __("Refresh"),
      glyph: NOC.glyph.refresh,
      scope: me,
      handler: me.onRefresh,
    });

    if(NOC.hasPermission("inv:sensor:update")){
      me.gridPlugins.push(
        Ext.create("Ext.grid.plugin.RowEditing", {
          clicksToEdit: 2,
          listeners: {
            scope: me,
            edit: me.onEdit,
            canceledit: me.onCancelEdit,
          },
        }),
      );
    }
    // Create stores
    me.sensorsStore = Ext.create("NOC.sa.managedobject.SensorsStore");
    Ext.apply(me, {
      items: [
        {
          xtype: "gridpanel",
          border: false,
          autoScroll: true,
          stateful: true,
          stateId: "sa.managedobject-sensors-grid",
          store: me.sensorsStore,
          columns: [
            {
              text: __("Local ID"),
              dataIndex: "local_id",
            },
            {
              text: __("Description"),
              dataIndex: "label",
              width: 250,
            },
            {
              text: __("Profile"),
              dataIndex: "profile",
              renderer: NOC.render.Lookup("profile"),
              editor: {
                xtype: "core.combo",
                restUrl: "/inv/sensorprofile/lookup/",
                uiStyle: "medium-combo",
              },
            },
            {
              text: __("Labels"),
              dataIndex: "labels",
              renderer: NOC.render.LabelField,
              editor: "labelfield",
              width: 200,
            },
            {
              text: __("Units"),
              dataIndex: "units",
              renderer: NOC.render.Lookup("units"),
            },
            {
              text: __("State"),
              dataIndex: "state",
              renderer: NOC.render.Lookup("state"),
              width: 200,
            },
            {
              text: __("Last Seen"),
              dataIndex: "last_seen",
              renderer: NOC.render.DateTime,
              width: 200,
            },
            {
              text: __("SNMP OID"),
              dataIndex: "snmp_oid",
              width: 200,
            },
            {
              text: __("IPMI ID"),
              dataIndex: "ipmi_id",
            },
            {
              text: __("Modbus Register"),
              dataIndex: "modbus_register",
            },
          ],
          viewConfig: {
            getRowClass: Ext.bind(me.getRowClass, me),
            listeners: {
              scope: me,
              cellclick: me.onCellClick,
            },
          },
          plugins: me.gridPlugins,
        },
      ],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [
            me.getCloseButton(),
            me.refreshButton,
          ],
        },
      ],
    });
    me.callParent();
  },
  //
  preview: function(record){
    var me = this;
    me.callParent(arguments);
    me.setTitle(Ext.String.format("{0} {1}", record.get("name"), __("Sensors")));
    Ext.Ajax.request({
      url: "/inv/sensor/?managed_object=" + record.get("id"),
      method: "GET",
      scope: me,
      success: function(response){
        var me = this,
          data = Ext.decode(response.responseText);
        // Load data
        me.sensorsStore.loadData(data || []);
      },
      failure: function(request){
        NOC.error(__("Failed to load data") + ": " + request.statusText);
      },
    });
  },
  //
  onRefresh: function(){
    var me = this;
    me.preview(me.currentRecord);
  },
  // Return Grid's row classes
  getRowClass: function(record){
    var me = this;
    if(me.rowClassField){
      var c = record.get(me.rowClassField);
      if(c){
        return c;
      } else{
        return "";
      }
    } else{
      return "";
    }
  },
  //
  onEdit: function(editor, e){
    var me = this,
      r = e.record,
      data = {
        profile: r.get("profile"),
        labels: r.get("labels"),
      };
    Ext.Ajax.request({
      url: "/inv/sensor/" + r.get("id") + "/",
      method: "PUT",
      jsonData: data,
      scope: me,
      success: function(){
        me.onRefresh();
        NOC.info(__("Saved"));
      },
      failure: function(){
        NOC.error(__("Failed to set data"));
      },
    });
  },
  //
  onCancelEdit: function(editor, context){
    if(context.record.phantom){
      context.grid.store.removeAt(context.rowIdx);
    }
  },
  //
  onCellClick: function(view, cell, cellIndex, record, row,
    rowIndex, e){
    var me = this;
    if(e.target.tagName === "A"){
      var header = view.panel.headerCt.getHeaderAtIndex(cellIndex);
      if(header.onClick){
        header.onClick.apply(me, [record]);
      }
    }
  },
});
