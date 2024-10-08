//---------------------------------------------------------------------
// inv.inv.plugins.rack Controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.rack.Controller");

Ext.define("NOC.inv.inv.plugins.rack.Controller", {
  extend: "Ext.app.ViewController",
  alias: "controller.rack",
  mixins: [
    "NOC.core.mixins.SVGInteraction",
  ],
  //
  onDataChanged: function(store){
    var viewModel = this.getViewModel();
    if(viewModel){
      viewModel.set("totalCount", store.getCount());
    }
  },
  //
  onCellValidateEdit: function(){
    return true;
  },
  //
  onCellEdit: function(editor, context){
    var me = this,
      viewModel = me.getViewModel();
    if(context.field === "position_front"){
      context.record.set("position_rear", 0);
    }
    if(context.field === "position_rear"){
      context.record.set("position_front", 0);
    }
    // Submit
    Ext.Ajax.request({
      url: "/inv/inv/" + viewModel.get("currentId") + "/plugin/rack/rackload/",
      method: "POST",
      scope: me,
      jsonData: {
        cid: context.record.get("id"),
        position_front: context.record.get("position_front"),
        position_rear: context.record.get("position_rear"),
        shift: context.record.get("shift"),
      },
      loadMask: me,
      success: function(){
        me.onReload();
      },
      failure: function(){
        NOC.error(__("Failed to save"));
      },
    });
  },
  //
  onAfterRender: function(container){
    var app = this.getView().up("[appId=inv.inv]"),
      svgObject = container.getEl().dom.querySelector("#svg-object");
    this.addInteractionEvents(app, svgObject, app.showObject.bind(app));

  },
  //
  onReload: function(){
    var me = this,
      viewModel = me.getViewModel();
    Ext.Ajax.request({
      url: "/inv/inv/" + viewModel.get("currentId") + "/plugin/rack/",
      method: "GET",
      scope: me,
      success: function(response){
        me.getView().preview(Ext.decode(response.responseText));
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  //
  onRearPressed: function(){
    var me = this,
      viewModel = me.getViewModel();
    viewModel.set("side", "rear");
    me.onReload();
  },
  //
  onFrontPressed: function(){
    var me = this,
      viewModel = me.getViewModel();
    viewModel.set("side", "front");
    me.onReload();
  },
  //
  onZoom: function(combo){
    var me = this.getView(),
      img = me.down("#image"),
      imgEl = img.getEl().dom;
    imgEl.style.transformOrigin = "0 0";
    imgEl.style.transform = "scale(" + combo.getValue() + ")";
  },
  //
  onDownloadSVG: function(){
    var me = this,
      vm = me.getViewModel(),
      side = vm.get("side"),
      currentId = vm.get("currentId"),
      svg = vm.getView().down("#viewPanel").getEl().dom.querySelector("object").contentDocument.documentElement.outerHTML,
      blob = new Blob([svg], {type: "image/svg+xml"}),
      url = URL.createObjectURL(blob),
      a = document.createElement("a");
    a.href = url;
    a.download = `rack-${side}-${currentId}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  },
});
