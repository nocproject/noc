//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.DurationFilterRow");

Ext.define("NOC.fm.alarm.view.grids.DurationFilterRow", {
  extend: "Ext.container.Container",
  alias: "widget.fm.alarm.filter.duration.row",
  controller: "fm.alarm.filter.duration.row",
  requires: [
    "NOC.fm.alarm.view.grids.DurationFilterRowController",
  ],
  viewModel: {
    data: {
      row: {
        duration: null,
        opacity: null,
      },
    },
    stores: {
      durationStore: {
        fields: ["value", "text"],
        data: [
          {"value": 1, "text": "1 " + __("min")},
          {"value": 5, "text": "5 " + __("min")},
          {"value": 10, "text": "10 " + __("min")},
          {"value": 15, "text": "15 " + __("min")},
          {"value": 30, "text": "30 " + __("min")},
          {"value": 60, "text": "60 " + __("min")},
          {"value": 1440, "text": "1440 " + __("min")},
        ],
      },
      opacityStore: {
        fields: ["value", "text"],
        data: [
          {"value": 1, "text": "0.3"},
          {"value": 2, "text": "0.5"},
          {"value": 3, "text": "0.7"},
          {"value": 4, "text": "1"},
        ],
      },
    },
  },
  config: {
    value: null,
  },
  twoWayBindable: [
    "value",
  ],
  layout: "hbox",
  padding: "5 0 5",
  defaults: {
    xtype: "combo",
    queryMode: "local",
    valueField: "value",
    width: 130,
  },
  items: [
    {
      name: "opacity",
      forceSelection: true,
      bind: {
        store: "{opacityStore}",
        value: "{row.opacity}",
      },
      editable: false,
      listeners: {
        select: "onSelect",
      },
    },
  ],
  initComponent: function(){
    if(this.lastRow){
      this.items = [
        {
          xtype: "displayfield",
          width: 137,
          padding: "0 5 0 0",
          value: __("Other"),
        },
      ].concat(this.items);
    } else{
      this.items = [
        {
          xtype: "displayfield",
          width: 7,
          padding: "0 5 0 0",
          value: "<",
        },
        {
          name: "duration",
          bind: {
            store: "{durationStore}",
            value: "{row.duration}",
          },
          editable: false,
          validator: function(value){
            var num = Number(value.replace(__("min"), "").trim());
            return !isNaN(num) && num > 0;
          },
          listeners: {
            select: "onSelect",
          },
        },
      ].concat(this.items);
    }
    this.callParent();
  },
  setValue: function(value, skip){
    // console.log("DurationFilterRow setValue : ", value);
    this.callParent([value]);
    if(!skip){
      // from viewModel
      this.setWidgetValues(value);
    }
  },
  setWidgetValues: function(data){
    // console.log("DurationFilterRow setWidgetValues : ", data);
    if(Ext.Object.isEmpty(data)){
      return;
    }
    this.getViewModel().set("row", data);
    // this.down("[name=opacity]").setValue(data.opacity);
    // if(this.down("[name=duration]")) {
    //     this.down("[name=duration]").setValue(data.duration);
    // }
  },
});