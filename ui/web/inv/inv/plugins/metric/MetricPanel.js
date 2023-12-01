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
              text: __("Value"),
              dataIndex: "value",
              renderer: function (value) {
                return Ext.String.format(
                  '<div style="height: 100%; display: flex; align-items: center;"><svg max-width="100%" m-height="100%" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="{0}" /></svg></div>',
                  value
                );
              },
              // renderer: function (
              // value,
              // metaData,
              // record,
              // rowIndex,
              // colIndex,
              // store,
              // view
              // ) {
              // const column = this.getColumns()[colIndex],
              //   row = this.getRows()[rowIndex],
              //   height = row.getHeight(),
              //   width = column.getWidth();
              // console.log(height, width);
              // return (
              // '<div style="width: 100%; height: 100%;display: flex; align-items: center; justify-content: center;">' +
              // '<svg style="width: 100%' +
              // width +
              // "; height: 100%" +
              // height +
              // '<svg preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">' +
              // '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#000">' +
              // value +
              // "</text>" +
              // "</svg>" +
              // "</div>"
              // );
              // },
              // renderer: this.generateSVGCode,
            },
            {
              text: __("Units"),
              dataIndex: "units__label",
            },
            {
              text: __("Alarm"),
              dataIndex: "oper_state__label",
            },
            {
              xtype: "widgetcolumn",
              width: 100,
              widget: {
                xtype: "button",
                text: __("Graph"),
                handler: function (btn) {
                  // var record = btn.getWidgetRecord();
                  // var dataIndex = btn.getWidgetColumn().dataIndex;
                  // var value = record.get(dataIndex);
                  window.open("http://127.0.0.1", "_blank");
                },
              },
            },
          ],
          features: [me.groupingFeature],
          viewConfig: {
            enableTextSelection: true,
          },
        },
      ],
    });
    me.callParent();
  },
  preview: function (data) {
    var me = this;
    me.currentId = data.id;
    me.store.loadData(data);
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
  generateSVGCode: function (value) {
    var svgCode = '<svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">';

    // Размеры и позиции элементов
    var widthPercent = 100;
    var heightPercent = 100;
    var scaleHeightPercent = 10;
    var limitLineHeightPercent = 20;

    // Цвета
    var criticalColor = "#FF0000";
    var warningColor = "#FFFF00";
    var normalColor = "#00FF00";
    var scaleColor = "#000000";
    var limitLineColor = "#000000";

    // Вычисление позиции пределов
    var criticalLimitPercent = 30;
    var warningLimitPercent = 70;

    // Отображение шкалы
    // svgCode +=
    //   '<rect x="0" y="' +
    //   (100 - scaleHeightPercent) +
    //   '%" width="' +
    //   widthPercent +
    //   '%" height="' +
    //   scaleHeightPercent +
    //   '%" fill="' +
    //   scaleColor +
    //   '"></rect>';

    // Отображение пределов
    // svgCode +=
    //   '<line x1="' +
    //   criticalLimitPercent +
    //   '%" y1="0" x2="' +
    //   criticalLimitPercent +
    //   '%" y2="' +
    //   limitLineHeightPercent +
    //   '%" stroke="' +
    //   limitLineColor +
    //   '"></line>';
    // svgCode +=
    //   '<line x1="' +
    //   warningLimitPercent +
    //   '%" y1="0" x2="' +
    //   warningLimitPercent +
    //   '%" y2="' +
    //   limitLineHeightPercent +
    //   '%" stroke="' +
    //   limitLineColor +
    //   '"></line>';

    // Отображение цветовых зон
    svgCode +=
      '<rect x="0" y="0" width="' +
      criticalLimitPercent +
      '%" height="' +
      scaleHeightPercent +
      '%" fill="' +
      criticalColor +
      '"></rect>';
    svgCode +=
      '<rect x="' +
      criticalLimitPercent +
      '%" y="0" width="' +
      (warningLimitPercent - criticalLimitPercent) +
      '%" height="' +
      scaleHeightPercent +
      '%" fill="' +
      warningColor +
      '"></rect>';
    svgCode +=
      '<rect x="' +
      warningLimitPercent +
      '%" y="0" width="' +
      (100 - warningLimitPercent) +
      '%" height="' +
      scaleHeightPercent +
      '%" fill="' +
      normalColor +
      '"></rect>';

    // Отображение значения параметра
    svgCode +=
      '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="' +
      scaleColor +
      '">' +
      value +
      "</text>";

    svgCode += "</svg>";

    return svgCode;
  },
});
//<svg
//  style="width: 100%; height: 100%;"
//  preserveAspectRatio="none"
//  xmlns="http://www.w3.org/2000/svg">
//  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#000">28</text>
//</svg>
