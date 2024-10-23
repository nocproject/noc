//---------------------------------------------------------------------
// main.home application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.home.Application");

Ext.define("NOC.main.home.Application", {
  extend: "NOC.core.Application",
  padding: 10,
  layout: "auto",
  baseCls: "noc-home-container",
  scrollable: true,
  smallHeight: 90,
  normalHeight: 200,
  extraHeight: 310,
  doubleHeight: 420,
  listeners: {
    render: function(panel){
      panel.up().mask(__("Loading..."));
      Ext.Ajax.request({
        method: "GET",
        url: "/main/home/dashboard/",
        scope: this,
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(Object.prototype.hasOwnProperty.call(data, "widgets") && !Ext.isEmpty(data.widgets)){
            var html = "";
            Ext.Array.each(data.widgets, function(widget){
              switch(widget.type){
                case "favorites":
                  var fav = "<ul style='list-style-type: none;margin: 0;padding-left: 5px'>";
                  Ext.each(widget.data.items, function(item){
                    fav += "<li><a href='" + item.link + "'>" + item.title
                                  + "</a></li><ul style='list-style-type: none;margin: 0;padding-left: 5px'>";
                    Ext.each(item.items, function(subitem){
                      fav += "<li><a href='" + subitem.link + "'>" + subitem.text + "</a></li>";
                    });
                    fav += "</ul>";
                  });
                  fav += "</ul>";
                  html += this.createWidget(widget.title, fav);
                  break;
                case "summary":
                  var rows = Ext.Array.map(widget.items, function(item){
                    var value = item.value;
                    if(Object.prototype.hasOwnProperty.call(item, "link")){
                      value = "<a href='" + item.link + "'>" + item.value + "</a>";
                    }
                    return "<tr class='noc-home-summary-select'><td>" + item.text + "</td><td style='padding-left: 5px;text-align: right;'>" + value + "</td></tr>";
                  });
                  html += this.createWidget(widget.title, "<table style='width: 100%;font-size: inherit;'>" + rows.join("") + "</table>");
                  break;
                case "text":
                  html += this.createWidget(widget.title, widget.data.text);
                  break;
              }
            }, this);
            panel.setHtml(html);
          }
        },
        failure: function(){
          NOC.error(__("Failed to get home data"));
        },
        callback: function(){
          panel.up().unmask();
        },
      });
    },
  },
  makeHeader: function(title){
    return `<div class="noc-home-widget-header x-panel-header x-header x-panel-header-default x-horizontal x-panel-header-horizontal x-panel-header-default-horizontal">\
              <div class="x-box-inner" style="height: 20px;">\
                  <div class="x-title x-panel-header-title x-panel-header-title-default x-box-item x-title-default x-title-rotate-none x-title-align-left">\
                    <div class="x-title-text x-title-text-default x-title-item" unselectable="on">${title}</div>\
                  </div>\
              </div>\
            </div>`;
  },
  makeContent: function(content){
    return `<div class="noc-home-widget-content">${content}</div>`;
  },
  createWidget: function(title, content){
    return `<div class="noc-home-widget">${this.makeHeader(title)}${this.makeContent(content)}</div>`;
  },
});
