//---------------------------------------------------------------------
// inv.inv Metric Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.metric.MetricPanel");

Ext.define("NOC.inv.inv.plugins.metric.MetricPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.metric.MetricModel",
  ],
  title: __("Metric"),
  closable: false,
  itemId: "metricPanel",
  border: false,
  initComponent: function() {
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
          text: __("Refresh"),
          scope: me,
          handler: me.refreshMetric
        },
        {
          enableToggle: true,
          itemId: "rangesBtn",
          text: __("Ranges") + ": " + __("Relative"),
          handler: me.rangeStyleToggle
        },
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
              renderer: this.valueRenderer,
              editor: {
                xtype: "textfield"
              }
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
                handler: function(btn) {
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
          listeners: {
            scope: me,
            celldblclick: function(grid, td, cellIndex, record, tr, rowIndex, e, eOpts) {
              var metricPanel = this;
              if(Ext.isEmpty(record.get("thresholds"))) {
                return;
              }
              var popupWindow = Ext.create('Ext.window.Window', {
                title: __("Edit Thresholds"),
                modal: true,
                items: [
                  {
                    xtype: "form",
                    scrollable: "y",
                    layout: "vbox",
                    defaults: {
                      xtype: "container",
                    },
                    tbar: [
                      {
                        text: __("Save"),
                        handler: function() {
                          var me = this,
                            url = Ext.String.format("/inv/inv/{0}/plugin/metric/{1}/set_threshold/", record.get("object"), record.get("id")),
                            values = me.up("form").getValues(),
                            body = {thresholds: Ext.Object.getKeys(values).map(function(el) {return {name: el, value: values[el]}})};

                          Ext.Ajax.request({
                            url: url,
                            method: "POST",
                            scope: me,
                            jsonData: body,
                            success: function() {
                              metricPanel.refreshMetric();
                              NOC.info(__("Thresholds has been updated"));
                              me.up("window").close();
                            },
                            failure: function() {
                              NOC.error(__("Thresholds update failed"));
                            }
                          });
                        },
                      },
                      {
                        text: __("Cancel"),
                        handler: function() {
                          this.up("window").close();
                        },
                      },
                    ],
                    items: Ext.Array.map(record.get("thresholds"), function(threshold) {
                      return {
                        layout: "column",
                        padding: "10 10 0 10",
                        defaults: {
                          columnWidth: 0.5,
                        },
                        items: [
                          {
                            xtype: "displayfield",
                            minWidth: 200,
                            maxWidth: 500,
                            value: threshold.label
                          },
                          {
                            xtype: "numberfield",
                            name: threshold.name,
                            value: threshold.value,
                          }
                        ]
                      }
                    })
                  }
                ]
              });
              popupWindow.show();
            },
          }
        },
      ],
    });
    me.callParent();
  },
  preview: function(data, objectId) {
    var me = this;
    me.currentId = objectId;
    me.store.loadData(data);
  },
  refreshMetric: function() {
    var me = this;

    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/metric/",
      method: "GET",
      scope: me,
      success: function(response) {
        var data = Ext.decode(response.responseText);
        me.preview(data, me.currentId);
      },
      failure: function() {
        NOC.error(__("Failed to get data for plugin") + " metric");
      }
    });
  },
  rangeStyleToggle: function(btn) {
    if(btn.pressed) {
      btn.setText(__("Ranges") + ": " + __("Absolute"),);
    } else {
      btn.setText(__("Ranges") + ": " + __("Relative"),);
    }
    this.up("[itemId=metricPanel]").down("[xtype=grid]").getView().refresh();
  },
  collapseAll: function() {
    this.up("[itemId=metricPanel]").groupingFeature.collapseAll();
  },
  expandAll: function() {
    this.up("[itemId=metricPanel]").groupingFeature.expandAll();
  },
  valueRenderer: function(value, metaData, record, rowIndex, colIndex, store, view) {
    var val, result = "",
      rangeStyle = this.up().down('[itemId=rangesBtn]').pressed,
      percent = (Math.abs(record.get("max_value")) + Math.abs(record.get("min_value"))) / 100;
    if(Ext.isEmpty(record.get("min_value")) || Ext.isEmpty(record.get("max_value"))) {
      return value
    }
    if(Ext.isEmpty(record.get("ranges"))) {
      return value
    }

    val = rangeStyle ? (value - record.get("min_value")) / percent : record.get("relative_position");
    result += "<div data-value='" + value + "' class='noc-metric-value' style='left:" + val + "%'></div>";
    result += "<div class='noc-metric-container'>";
    result += "<div class='noc-metric-range noc-metric-green-range'></div>";
    Ext.each(record.get("ranges"), function(range) {
      var start = rangeStyle ? ((range.left - record.get("min_value")) / percent) : range.relative_position.left,
        end = rangeStyle ? ((range.right - record.get("min_value")) / percent) : range.relative_position.right;
      result += "<div class='noc-metric-range' style='left: " + start + "%; width: " + (end - start) + "%; background: " + range.color + ";'></div>";
    });
    if(!Ext.isEmpty(record.get("thresholds"))) {
      Ext.each(record.get("thresholds"), function(threshold) {
        var position = rangeStyle ? ((threshold.value - record.get("min_value")) / percent) : threshold.relative_position;
        result += "<div class='noc-metric-tick' data-qtip='" + threshold.value + " : " + threshold.description + "' style='left: " + position + "%'></div>";
      });
    }
    result += "</div>";
    return result;
  }
});
