//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.DurationFilter");

Ext.define("NOC.fm.alarm.view.grids.DurationFilter", {
  extend: "Ext.form.FieldContainer",
  itemId: "fm-alarm-duration-filter",
  alias: "widget.fm.alarm.filter.duration",
  controller: "fm.alarm.filter.duration",
  requires: [
    "NOC.fm.alarm.view.grids.DurationFilterController",
    "NOC.fm.alarm.view.grids.DurationFilterRow",
  ],
  viewModel: {
    data: {},
  },
  config: {
    value: null,
  },
  twoWayBindable: [
    "value",
  ],
  layout: "vbox",
  items: [
    {
      xtype: "checkboxfield",
      boxLabel: __("Switch Off"),
      name: "on",
      listeners: {
        change: "onChangeValue",
      },
    },
    {
      xtype: "fm.alarm.filter.duration.row",
      name: "row1",
      listeners: {
        valuechanged: "onChangeValue",
      },
    },
    {
      xtype: "fm.alarm.filter.duration.row",
      name: "row2",
      listeners: {
        valuechanged: "onChangeValue",
      },
    },
    {
      xtype: "fm.alarm.filter.duration.row",
      name: "row3",
      listeners: {
        valuechanged: "onChangeValue",
      },
    },
    {
      xtype: "fm.alarm.filter.duration.row",
      lastRow: true,
      name: "row4",
      listeners: {
        valuechanged: "onChangeValue",
      },
    },
  ],
  initValues: {
    on: false,
    row1: {
      duration: 1,
      opacity: 1,
    },
    row2: {
      duration: 15,
      opacity: 4,
    },
    row3: {
      duration: 30,
      opacity: 3,
    },
    row4: {
      opacity: 2,
    },
  },
  initComponent: function(){
    this.callParent();
    this.setWidgetValues(this.getInitValues());
  },
  //
  setValue: function(value, skip){
    this.callParent([value]);
    if(!skip){
      this.setWidgetValues(value);
    }
  },
  setWidgetValues: function(data){
    var me = this, setIf = function(key){
      if(Object.prototype.hasOwnProperty.call(data, key)){
        me.getViewModel().set(key, data[key]);
        me.down("[name=" + key + "]").setValue(data[key]);
      }
    };
    if(Ext.Object.isEmpty(data)){
      return;
    }
    Ext.each(["on", "row1", "row2", "row3", "row4"], setIf);
  },
  getInitValues: function(){
    return Ext.clone(this.initValues);
  },
});