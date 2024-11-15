//---------------------------------------------------------------------
// Validation plugin
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.plugins.Validation");

Ext.define("NOC.fm.alarm.plugins.Validation", {
  extend: "Ext.panel.Panel",
  title: __("Validation"),
  app: null,
  autoScroll: true,
  bodyPadding: 4,
  layout: "border",
  border: false,
  detailTpl: Ext.create("Ext.Template", [
    "<div style='border-bottom: 1px solid gray'>",
    "<b>Subject:</b> {subject}",
    "</div>",
    "<pre>{body}</pre>",
  ]),

  initComponent: function(){
    var me = this;

    me.store = Ext.create("Ext.data.Store", {
      fields: [
        "uuid", "subject", "body",
        {
          name: "introduced",
          type: "date",
        },
        {
          name: "changed",
          type: "date",
        },
        "cls",
      ],
      data: [],
    });

    me.selectGrid = Ext.create("Ext.grid.Panel", {
      //autoScroll: true,
      store: me.store,
      columns: [
        {
          dataIndex: "subject",
          text: __("Subject"),
          flex: 1,
        },
        {
          dataIndex: "cls",
          text: __("Error Type"),
          width: 200,
        },
        {
          dataIndex: "introduced",
          text: __("Introduced"),
          width: 150,
          renderer: NOC.render.DateTime,
        },
        {
          dataIndex: "changed",
          text: __("Changed"),
          width: 150,
          renderer: NOC.render.DateTime,
        },
      ],
      height: 200,
      forceFit: true,
      region: "north",
      listeners: {
        scope: me,
        selectionchange: me.onSelectionChange,
      },
    });

    me.detailPanel = Ext.create("Ext.panel.Panel", {
      region: "center",
      bodyPadding: 8,
      html: "Please select an error to see details",
    });

    Ext.apply(me, {
      items: [
        me.selectGrid,
        me.detailPanel,
      ],
    });

    me.callParent();
  },

  updateData: function(data){
    var me = this;
    me.store.loadData(data.validation_errors);
  },

  onSelectionChange: function(sm, record){
    var me = this;
    if(record.length){
      me.detailPanel.update(
        me.detailTpl.apply(record[0].data),
      );
    }
  },
});


