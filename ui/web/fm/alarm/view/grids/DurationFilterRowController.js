//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.DurationFilterRowController");
Ext.define("NOC.fm.alarm.view.grids.DurationFilterRowController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.alarm.filter.duration.row",
  // valuesBinding: undefined,
  // init: function(view) {
  //     var viewModel = view.getViewModel();
  //     this.valuesBinding = viewModel.bind({
  //         bindTo: "{values}",
  //         deep: true
  //     }, this.onChangeValues, this);
  // },
  // destroy: function() {
  //     this.valuesBinding.destroy();
  // },
  // onChangeValues: function(data) {
  //     console.log("Duration row :", data);
  //     // this.getView().setValue(data, true);
  // },
  onSelect: function(self){
    if(self.isValid()){
      var values = this.getViewModel().get("row");
      this.getView().setValue(values, true);
      this.fireViewEvent("valuechanged");
    }
  },
});