//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.ProfileFilterController");
Ext.define("NOC.fm.alarm.view.grids.ProfileFilterController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.alarm.profile.filter",
  onDataUpdated: function(store){
    var records = store.data.items,
      mapping = function(record){
        return {
          profileId: record.get("profileId"),
          condition: record.get("condition"),
          // include: record.get("include"),
          value: record.get("value"),
        }
      };
    if(this.isEmpty(records)){
      this.getView().setValue([], true);
    }
    if(this.isValid(records)){
      this.getView().setValue(records.map(mapping), true);
    }
  },
  onChangeWidget: function(field){
    field.getWidgetRecord().set(field.dataIndex, field.getValue());
  },
  isValid: function(records){
    var i, len = records.length;
    for(i = 0; i < len; i++){
      if(!this.isRowValid(records[i].data)){
        return false;
      }
    }
    return true;
  },
  isRowValid: function(data){
    if(data.value == null || data.value < 0){
      return false;
    }
    if(!data.profileId){
      return false;
    }
    return data.condition;

  },
  isEmpty: function(records){
    if(records.length !== 1){
      return false;
    }
    return !records[0].get("value") && !records[0].get("condition") && !records[0].get("profileId");
  },
});