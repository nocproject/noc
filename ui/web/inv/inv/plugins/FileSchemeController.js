//---------------------------------------------------------------------
// inv.inv.plugins FileController
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.FileSchemeController");

Ext.define("NOC.inv.inv.plugins.FileSchemeController", {
  extend: "Ext.app.ViewController",
  alias: "controller.filescheme",
  mixins: [
    "NOC.inv.inv.plugins.Mixins",
  ],
  onReload: function(saveZoom){
    var me = this,
      vm = me.getViewModel(),
      view = me.getView(),
      maskComponent = me.getView().up("[appId=inv.inv]").maskComponent,
      messageId = maskComponent.show("reloading", ["scheme"]),
      name = view.itemId.replace("Panel", "").toLowerCase();
    Ext.Ajax.request({
      url: "/inv/inv/" + vm.get("currentId") + "/plugin/" + name + "/",
      method: "GET",
      scope: me,
      success: function(response){
        var zoomControl = view.down("#zoomControl");
        view.preview(Ext.decode(response.responseText));
        if(saveZoom === true){
          zoomControl.restoreZoom();
        } else{
          zoomControl.reset();
        }
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
      callback: function(){
        maskComponent.hide(messageId);
      },
    });
  },
  //
  onSideChange: function(side){
    var me = this,
      viewModel = me.getViewModel();
    viewModel.set("side", side);
    me.onReload(true);
  },
  // set context
  onDownloadSVG: function(){
    Ext.bind(this.downloadSVG, this.getView())();
  },
  //
  onSchemeClick: function(evt, target){
    var findSelectableAncestor = function(element){
        while(element && element !== document.body){
          if(element.classList.contains('selectable')){
            return element;
          }
          element = element.parentElement;
        }
        return undefined;
      },
      element = findSelectableAncestor(target);
    
    if(Ext.isEmpty(element)) return

    var container = this.getView(),
      app = container.up("[appId=inv.inv]"),
      events = element.dataset.interaction.split(",");
    Ext.each(events, function(e){
      var [, action, resource] = e.split(":"),
        resourceData = decodeURIComponent(resource);
      if(action === "go"){
        var value = resourceData.split(":")[1];
        app.showObject(value);
      }
      if(action === "info"){
        this.showBalloon(app, "schemeBalloon", resourceData, [evt.pageX, evt.pageY]);
      }
    }, this);
  },
});
