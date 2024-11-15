//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.DurationFilterController");
Ext.define("NOC.fm.alarm.view.grids.DurationFilterController", {
  extend: "Ext.app.ViewController",
  alias: "controller.fm.alarm.filter.duration",
  onChangeValue: function(self){
    var widgetValue = Ext.clone(this.getViewModel().get("displayFilter.duration")) || this.getView().getInitValues();
    widgetValue[self.name] = self.getValue();
    if(this.validate(self, widgetValue)){
      this.getView().setValue(widgetValue, true);
    }
  },
  validate: function(self, widgetValue){
    if(self.name === "on"){
      return true;
    }
    if(widgetValue.on){
      return true;
    }
  },
  // valuesBinding: undefined,
  // init: function(view) {
  //     console.log("DurationFilter init");
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
  //     console.log("Duration onChangeValues :", data);
  //     this.getView().setValue(data, true);
  // }
});