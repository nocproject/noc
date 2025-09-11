//---------------------------------------------------------------------
// NOC.core.mixins.Ballon
// show information balloon, go to object or channel and e.g. on click
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.mixins.Ballon");

Ext.define("NOC.core.mixins.Ballon", {
  showBalloon: function(app, itemId, resourceData, pos){
    var self = this;
    Ext.Ajax.request({
      url: "/inv/inv/baloon/",
      method: "POST",
      jsonData: {
        resource: resourceData,
      },
      success: function(response){
        var result = Ext.decode(response.responseText),
          tooltipConfig = {},
          path = Ext.Array.map(result.path || [], function(item){
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
                    `;

        Ext.ComponentQuery.query("tooltip#" + itemId).forEach(function(tooltip){
          tooltip.destroy();
        });
                      
        tooltipConfig = {
          itemId: itemId,
          title: (result.n_alarms > 0) ? "<i class='fa fa-exclamation-triangle' style='color:#f39c12;padding-right: 8px;'></i>" + result.title : result.title,
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
                  self.showInvObject(app, value);
                  tooltip.destroy();
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
                    if(button.scope === "o"){
                      self.showInvObject(app, button.args);
                    }
                    if(button.scope === "c"){
                      self.showChannel(app, button.args);
                    }
                  }
                  tooltip.destroy();
                },
              }
            }),
          });
        }

        var tooltip = Ext.create("Ext.tip.ToolTip", tooltipConfig);
        tooltip.showAt(pos);
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  //
  showInvObject: function(app, value){
    if(Ext.isFunction(app.showObject)){
      app.showObject(value);
    } else{
      NOC.launch("inv.inv", "history", {
        args: [value],
      });
    }
  },
  //
  showChannel: function(app, value){
    if(Ext.isFunction(app.onMap)){
      app.currentRecord = {id: value};
      app.onMap(value);
    } else{
      NOC.launch("inv.channel", "history", {
        args: [value],
        "override": [
          {
            "showGrid": function(){
              this.up().close();
            },
          },
          {
            "onEditRecord": function(){
              this.currentRecord = {id: value};
              this.onMap();
            },
          },
          {
            "onCloseMap": function(){
              this.up().close();
            },
          },
        ],
      });
    }
  },
});