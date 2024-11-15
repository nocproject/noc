//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.ProfileFilter");

Ext.define("NOC.fm.alarm.view.grids.ProfileFilter", {
  extend: "Ext.form.FieldContainer",
  alias: "widget.fm.alarm.filter.profile",
  controller: "fm.alarm.profile.filter",
  itemId: "fm-alarm-filter-profile",
  requires: [
    "NOC.fm.alarm.view.grids.ProfileFilterController",
    "NOC.fm.alarm.store.Profile",
  ],
  conditionWidth: 55,
  valueWidth: 75,
  config: {
    value: null,
  },
  twoWayBindable: [
    "value",
  ],
  initValues: [
    {
      profileId: "",
      condition: "",
      value: 0,
    },
  ],
  viewModel: {
    stores: {
      conditionStore: {
        fields: [
          {name: "profileId", type: "string"},
          {name: "condition", type: "string"},
          {name: "value", type: "int"},
        ],
        listeners: {
          update: "onDataUpdated",
        },
        data: [],
      },
    },
  },
  items: {
    xtype: "grid",
    header: false,
    hideHeaders: true,
    border: false,
    bind: {store: "{conditionStore}"},
    columns: [
      {
        xtype: "widgetcolumn",
        dataIndex: "profileId",
        flex: 1,
        widget: {
          xtype: "combobox",
          valueField: "id",
          displayField: "label",
          // displayTpl doesn't work because the collapsed combo is just a simple <input> element that can't contain HTML
          // set the image as a background image to the <input>, may be
          // displayTpl: '<tpl for="."><i class="{icon}"></i><span style="padding-left: 3px">{label}</span></tpl>',
          editable: false,
          height: 22,
          tpl: "<ul class='x-list-plain'><tpl for='.'>" +
                        "<li role='option' class='x-boundlist-item'>" +
                        "<i class='{icon}'></i><span style='padding-left: 3px'>{label}</span></li>" +
                        "</tpl></ul>",
          listeners: {
            select: "onChangeWidget",
          },
          store: {
            type: "fm.profile",
          },
        },
      },
      {
        xtype: "widgetcolumn",
        dataIndex: "value",
        widget: {
          xtype: "numberfield",
          minValue: 0,
          listeners: {
            change: "onChangeWidget",
          },
        },
      },
      {
        xtype: "widgetcolumn",
        dataIndex: "condition",
        widget: {
          xtype: "combobox",
          displayField: "label",
          valueField: "id",
          editable: false,
          height: 22,
          listeners: {
            select: "onChangeWidget",
          },
          store: {
            fields: ["id", "label"],
            data: [
              {"id": "gt", "label": ">="},
              {"id": "lt", "label": "<="},
            ],
          },
        },
      },
      {
        xtype: "actioncolumn",
        width: 20,
        items: [{
          tooltip: __("Reset values"),
          iconCls: "x-fa fa-times-circle",
          handler: function(view, rowIndex, colIndex, item, e, record){
            var store = view.getStore(),
              component = view.up("[itemId=fm-alarm-filter-profile]");
            store.remove(record);
            if(store.getCount() < 1){
              var initValue = Ext.clone(component.getInitValues());
              store.add(Ext.create("Ext.data.Model", initValue));
            }
            component.getController().onDataUpdated(store);
          },
          isDisabled: function(view, rowIndex, colIndex, item, record){
            var controller = view.up("[itemId=fm-alarm-filter-profile]").getController();
            return !controller.isRowValid(record.data);
          },
        }],
      },
    ],
  },
  initComponent: function(){
    this.setWidth();
    this.callParent();
    this.setWidgetValues(this.getInitValues());
  },
  setValue: function(value, skip){
    this.callParent([value]);
    if(!skip){
      // from viewModel
      this.setWidgetValues(value);
    }
  },
  setWidgetValues: function(data){
    var mapping = function(item){
      return Ext.create("Ext.data.Model", {
        profileId: item.profileId,
        condition: item.condition,
        value: item.value,
        // include: item.include
      });
    };
    if(!Ext.Object.isEmpty(data)){
      if(!Ext.isArray(data)){
        data = [data];
      }
      this.getViewModel().getStore("conditionStore").loadRecords(data.map(mapping));
    }
    if(Ext.isArray(data) && data.length === 0){
      this.getViewModel().getStore("conditionStore").loadRecords(this.getInitValues().map(mapping));
    }
  },
  getInitValues: function(){
    return Ext.clone(this.initValues);
  },
  setWidth: function(){
    Ext.each(this.items.columns, function(col){
      if(col.dataIndex === "condition"){
        col.width = this.conditionWidth;
      } else if(col.dataIndex === "value"){
        col.width = this.valueWidth;
      }
    }, this);
  },
});