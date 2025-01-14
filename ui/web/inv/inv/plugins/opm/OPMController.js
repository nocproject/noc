//---------------------------------------------------------------------
// inv.inv OPM Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.opm.OPMController");

Ext.define("NOC.inv.inv.plugins.opm.OPMController", {
  extend: "Ext.app.ViewController",
  alias: "controller.opm",
  mixins: [
    "NOC.inv.inv.plugins.Mixins",
  ],
  collapseSettings: function(){
    this.lookupReference("opmRightPanel").toggleCollapse();
  },
  // onActivate: function(){
  //   console.log("OPM Panel activated");
  //   // this.onReload();
  //   console.log(this.generateIcon(true, "circle", NOC.colors.yes, __("online")));
  // },
  onComboboxSelect: function(){
    var vm = this.getViewModel(),
      group = vm.get("group"),
      band = vm.get("band");
    console.log("Combobox selected", group, band);
  },
  onReload: function(){
    var vm = this.getViewModel(),
      currentId = vm.get("currentId");
    if(Ext.isEmpty(currentId)) return;
    vm.set("icon", this.generateIcon(true, "spinner", "grey", __("loading")));
    Ext.Ajax.request({
      url: "/inv/inv/" + currentId + "/plugin/opm/data/",
      method: "GET",
      scope: this,
      params: {
        b: vm.get("band"),
        g: vm.get("group"),
      },
      success: function(response){
        var data = Ext.decode(response.responseText);
        console.log("Data loaded", data);
        vm.set("icon", this.generateIcon(true, "circle", NOC.colors.yes, __("online")));
      },
      failure: function(){
        vm.set("icon", this.generateIcon(true, "circle", NOC.colors.no, __("offline")));
        NOC.error(__("Failed to load data"));
      },
    });
  },
  startTimer: function(){
    var view = this.getView();
    view.observer = this.setObservable(view);
    view.timer = Ext.TaskManager.start({
      run: this.reloadTask,
      interval: 3000,
      args: [this.onReload, this.getViewModel(), "opm"],
      scope: view,
    });
  },
});