//---------------------------------------------------------------------
// inv.inv Metric Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.metric.MetricPanel");

Ext.define("NOC.inv.inv.plugins.metric.MetricPanel", {
  extend: "Ext.panel.Panel",
  requires: ["NOC.inv.inv.plugins.metric.MetricModel"],
  title: __("Metric"),
  closable: false,
  itemId: "metricPanel",
  border: false,
  saveBuffer: [],
  initComponent: function () {
    var me = this;
    me.groupingFeature = Ext.create("Ext.grid.feature.Grouping", {
      startCollapsed: false,
    });
    // Metric Store
    me.store = Ext.create("Ext.data.Store", {
      model: "NOC.inv.inv.plugins.metric.MetricModel",
      groupField: "component",
    });
    Ext.apply(me, {
      tbar: [
        // {
        //   text: __("Save"),
        //   glyph: NOC.glyph.save,
        //   handler: me.save,
        // },
        // {
        //   text: __("Mass"),
        //   itemId: "saveModeBtn",
        //   enableToggle: true,
        // },
        // {
        //   text: __("Reset"),
        //   glyph: NOC.glyph.eraser,
        //   handler: me.reset,
        // },
        "->",
        {
          text: __("Collapse All"),
          handler: me.collapseAll,
        },
        {
          text: __("Expand All"),
          handler: me.expandAll,
        },
      ],
      items: [
        {
          xtype: "grid",
          border: false,
          autoScroll: true,
          stateful: true,
          stateId: "inv.inv-metric-grid",
          bufferedRenderer: false,
          store: me.store,
          columns: [
            {
              text: __("Metric Type"),
              dataIndex: "name",
            },
            {
              text: __("Component"),
              dataIndex: "component__label",
            },
            {
              text: __("Value"),
              dataIndex: "value",
            },
            {
              text: __("Units"),
              dataIndex: "units__label",
            },
            {
              text: __("Alarm"),
              dataIndex: "oper_state__label",
            },
            // {
            // text: __("Scope"),
            // dataIndex: "scope__label",
            // },
            // {
            // text: __("Value"),
            // dataIndex: "value",
            // flex: 1,
            // editor: "textfield",
            // renderer: function (value, metaData, record) {
            // if (record.get("type") === "bool") {
            // if (value == null) {
            // value = false;
            // }
            // return NOC.render.Bool(value);
            // }
            // return value;
            // },
            // },
            // {
            // text: __("Description"),
            // dataIndex: "description",
            // },
          ],
          features: [me.groupingFeature],
          viewConfig: {
            enableTextSelection: true,
          },
          // listeners: {
          // scope: me,
          // edit: me.onEdit,
          // },
        },
      ],
    });
    me.callParent();
  },
  preview: function (data) {
    var me = this;
    me.currentId = data.id;
    me.store.loadData(data);
    me.down("[name=scope__label]").setStore({
      autoLoad: true,
      proxy: {
        type: "rest",
        url: "/inv/inv/" + data.id + "/plugin/metric/",
      },
    });
  },
  save: function () {
    var me = this.up("[itemId=metricPanel]");
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/metric/",
      method: "PUT",
      jsonData: me.saveBuffer,
      // scope: me,
      success: function (response) {
        me.onReload();
      },
      failure: function () {
        NOC.error(__("Failed to save"));
      },
    });
  },
  onReload: function () {
    var me = this;
    me.saveBuffer = [];
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/metric/",
      method: "GET",
      // scope: me,
      success: function (response) {
        me.preview(Ext.decode(response.responseText));
      },
      failure: function () {
        NOC.error(__("Failed to get data"));
      },
    });
  },
  reset: function () {
    var me = this.up("[itemId=metricPanel]");
    me.onReload();
  },
  collapseAll: function () {
    this.up("[itemId=metricPanel]").groupingFeature.collapseAll();
  },
  expandAll: function () {
    this.up("[itemId=metricPanel]").groupingFeature.expandAll();
  },
});
