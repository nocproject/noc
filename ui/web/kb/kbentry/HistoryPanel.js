//---------------------------------------------------------------------
// kb.entry HistoryPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.kb.kbentry.HistoryPanel");

Ext.define("NOC.kb.kbentry.HistoryPanel", {
  extend: "NOC.core.ApplicationPanel",
  app: null,
  autoScroll: true,
  historyHashPrefix: "history",

  initComponent: function(){
    var me = this;

    me.view = Ext.create("Ext.DataView", {
      fullscreen: true,
      store: {
        fields: ["timestamp", "user", "diff"],
        data: [],
      },
      itemTpl: "<div>{user}&nbsp;:&nbsp;{timestamp}</div><div>{diff}</div>",
    });
    Ext.apply(me, {
      items: [
        me.view,
      ],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [
            me.getCloseButton(),
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
    me.setTitle(record.get("subject") + " - " + __("history"));
    Ext.Ajax.request({
      url: "/kb/kbentry/" + record.get("id") + "/history/",
      method: "GET",
      scope: me,
      success: function(response){
        var result = Ext.decode(response.responseText);
        me.view.store.loadData(result.data);
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
});
