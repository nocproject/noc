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
  //
  downloadSVG: function(){
    Ext.bind(this.onDownloadSVG, this.getView())();
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
    events.forEach(function(e){
      var [, action, resource] = e.split(":"),
        resourceData = decodeURIComponent(resource);
      if(action === "go"){
        var value = resourceData.split(":")[1];
        app.showObject(value);
      }
      if(action === "info"){
        var messageId = app.maskComponent.show("fetching", ["balloon info "]);
        Ext.Ajax.request({
          url: "/inv/inv/baloon/",
          method: "POST",
          jsonData: {
            resource: resourceData,
          },
          success: function(response){
            var result = Ext.decode(response.responseText),
              tooltipConfig = {},
              path = Ext.Array.map(result.path, function(item){
                if(!item.id){
                  return `<span>${item.label}</span>`
                }
                return `<span style='cursor: pointer;text-decoration: underline;'`
                    + `data-item-id="${item.id}"`
                    + `>${item.label}</span>`
              }).join(" > "),
              tooltipHtml = `
                      ${path}
                      <div style='padding: 4px 0;'><em>${result.description}</em></div>
                    `

            Ext.ComponentQuery.query("tooltip#SVGbaloon").forEach(function(tooltip){
              tooltip.destroy();
            });
                      
            tooltipConfig = {
              itemId: "SVGbaloon",
              title: result.title,
              padding: "4 0",
              html: tooltipHtml,
              closeAction: "destroy",
              dismissDelay: 0,
              tools: [
                {
                  type: "close",
                  handler: function(){
                    tooltip.destroy();
                  },
                },
              ],
              listeners: {
                afterrender: function(tooltip){
                  var items = tooltip.el.query("[data-item-id]");
                  items.forEach(function(element){
                    element.addEventListener("click", function(evt){
                      var value = element.dataset.itemId;
                      evt.stopPropagation(); 
                      app.showObject(value);
                    }); 
                  });
                },
              },
            }
            if(result.buttons && result.buttons.length){
              Ext.apply(tooltipConfig, {
                buttons: Ext.Array.map(result.buttons, function(button){ 
                  return {
                    xtype: "button",
                    glyph: button.glyph,
                    tooltip: button.hint,
                    handler: function(){
                      if(button.action === "go"){
                        app.showObject(button.args);
                      }
                    },
                  }
                }),
              });
            }

            var tooltip = Ext.create("Ext.tip.ToolTip", tooltipConfig);
            tooltip.showAt([evt.pageX, evt.pageY]);
          },
          failure: function(){
            NOC.error(__("Failed to get data"));
          },
          callback: function(){
            app.maskComponent.hide(messageId);
          }, 
        });
      }
    });
  },
});
