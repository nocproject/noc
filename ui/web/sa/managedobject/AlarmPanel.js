//---------------------------------------------------------------------
// sa.managedobject AlarmPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.AlarmPanel");

Ext.define("NOC.sa.managedobject.AlarmPanel", {
  extend: "NOC.core.ApplicationPanel",
  alias: "widget.sa.alarms",
  requires: [
    "NOC.fm.alarm.Model",
  ],
  autoScroll: true,

  initComponent: function(){
    var me = this;

    me.refreshButton = Ext.create("Ext.button.Button", {
      text: __("Refresh"),
      glyph: NOC.glyph.refresh,
      scope: me,
      handler: me.onRefresh,
    });

    me.statusRadioButton = Ext.create("Ext.form.RadioGroup", {
      defaults: {
        padding: "0 10",
      },
      items: [
        {
          boxLabel: __("Active"),
          name: "params",
          inputValue: "status=A",
          checked: true,
        },
        {
          boxLabel: __("Archive (last 25)"),
          width: 150,
          name: "params",
          inputValue: 'status=C&__limit=25&__sort=[{"property":"timestamp","direction":"DESC"}]',
        },
      ],
      listeners: {
        scope: me,
        change: me.onRefresh,
      },
    });

    me.store = Ext.create("Ext.data.Store", {
      model: "NOC.fm.alarm.Model",
      data: [],
    });

    me.grid = Ext.create("Ext.grid.Panel", {
      store: me.store,
      stateful: true,
      stateId: "sa.managedobject-alarm",
      columns: [
        {
          text: __("ID"),
          dataIndex: "id",
          width: 150,
        },
        {
          text: __("Time"),
          dataIndex: "timestamp",
          width: 100,
          renderer: NOC.render.DateTime,
        },
        {
          text: __("Severity"),
          dataIndex: "severity",
          width: 70,
          renderer: NOC.render.Lookup("severity"),
        },
        {
          text: __("Class"),
          dataIndex: "alarm_class",
          width: 300,
          renderer: NOC.render.Lookup("alarm_class"),
        },
        {
          text: __("Subject"),
          dataIndex: "subject",
          flex: 1,
        },
        {
          text: __("Duration"),
          dataIndex: "duration",
          width: 70,
          align: "right",
          renderer: NOC.render.Duration,
        },
        {
          text: __("Events"),
          dataIndex: "events",
          width: 30,
          align: "right",
        },
      ],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [
            me.getCloseButton(),
            me.refreshButton,
            me.statusRadioButton,
          ],
        },
      ],
      viewConfig: {
        getRowClass: Ext.bind(me.getRowClass, me),
      },
      listeners: {
        scope: me,
        itemdblclick: me.onOpenAlarm,
      },
    });
    Ext.apply(me, {
      items: [
        me.grid,
      ],
    });
    me.callParent();
  },
  //
  preview: function(record){
    var me = this;
    me.callParent(arguments);
    var status = me.statusRadioButton.getValue().params,
      url = Ext.String.format("/fm/alarm/?managed_object={0}&__format=ext&{1}", me.currentRecord.get("id"), status);
    me.setTitle(record.get("name") + " alarms");
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: me,
      success: function(response){
        var result = Ext.decode(response.responseText);
        if(Object.hasOwn(result, "data")){
          me.store.loadData(result.data);
        } else{
          me.store.removeAll();
        }
      },
      failure: function(){
        NOC.error(__("Failed to load data"));
      },
    });
  },
  //
  onRefresh: function(){
    var me = this;
    me.preview(me.currentRecord);
  },
  //
  getRowClass: function(record){
    return record.get("row_class");
  },
  //
  onOpenAlarm: function(grid, record){
    NOC.launch(
      "fm.alarm", "history", {args: [record.get("id")]},
    );
  },
});
