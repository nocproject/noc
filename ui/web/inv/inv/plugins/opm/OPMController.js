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
  onComboboxSelect: function(){
    var vm = this.getViewModel(),
      group = vm.get("group"),
      band = vm.get("band");
    console.log("Combobox selected", group, band);
    this.onReload();
  },
  onReload: function(isReload){
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
        if(data.status){
          this.drawDiagram(data.power, vm.get("band"), isReload);
        }
        vm.set("icon", this.generateIcon(true, "circle", NOC.colors.yes, __("online")));
      },
      failure: function(){
        vm.set("icon", this.generateIcon(true, "circle", NOC.colors.no, __("offline")));
        NOC.error(__("Failed to load data"));
      },
    });
  },
  drawDiagram: function(data, band, isReload){
    var spectrogram = this.getView().lookup("opmDiagram"),
      height = spectrogram.getHeight(),
      width = spectrogram.getWidth();
    console.log(data, height, width);
    spectrogram.draw(data, band, isReload);
  },
  startTimer: function(){
    var view = this.getView(),
      interval = 3000;
    view.observer = this.setObservable(view);
    view.timer = Ext.TaskManager.start({
      run: this.reloadTask,
      interval: interval,
      args: [this.onReload, this.getViewModel(), "opm"],
      scope: view,
    });
  },
});