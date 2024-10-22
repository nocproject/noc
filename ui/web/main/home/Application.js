//---------------------------------------------------------------------
// main.home application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.home.Application");

Ext.define("NOC.main.home.Application", {
  extend: "NOC.core.Application",
  baseCls: "noc-home-container",
  padding: 10,
  scrollable: true,
  smallHeight: 90,
  normalHeight: 200,
  extraHeight: 310,
  doubleHeight: 420,
  listeners: {
    render: function(panel){
      panel.mask(__("Loading..."));
      Ext.Ajax.request({
        method: "GET",
        url: "/main/home/dashboard/",
        scope: this,
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(Object.prototype.hasOwnProperty.call(data, "widgets") && !Ext.isEmpty(data.widgets)){
            Ext.Array.each(data.widgets, function(widget){
              var items;
              switch(widget.type){
                case "favorites":
                  var html = "<ul style='list-style-type: none;margin: 0;padding-left: 5px'>";
                  Ext.each(widget.data.items, function(item){
                    html += "<li><a href='" + item.link + "'>" + item.title
                              + "</a></li><ul style='list-style-type: none;margin: 0;padding-left: 5px'>";
                    Ext.each(item.items, function(subitem){
                      html += "<li><a href='" + subitem.link + "'>" + subitem.text + "</a></li>";
                    });
                    html += "</ul>";
                  });
                  html += "</ul>";
                  items = [
                    {
                      xtype: "container",
                      margin: 4,
                      html: html,
                      listeners: {
                        render: function(p){
                          console.log(p.getWidth());
                        },
                      },
                    },
                  ];    
                  break;
                case "summary":
                  var rows = Ext.Array.map(widget.items, function(item){
                    var value = item.value;
                    if(Object.prototype.hasOwnProperty.call(item, "link")){
                      value = "<a href='" + item.link + "'>" + item.value + "</a>";
                    }
                    return "<tr class='noc-home-summary-select'><td>" + item.text + "</td><td style='padding-left: 5px;text-align: right;'>" + value + "</td></tr>";
                  });
                  html = "<table style='width: 100%'>" + rows.join("") + "</table>"; 
                  items = [
                    {
                      xtype: "container",
                      margin: 4,
                      html: "<table style='width: 100%'>" + rows.join("") + "</table>",
                      listeners: {
                        render: function(p){
                          console.log(p.getWidth());
                        },
                      },
                    },
                  ];    
                  break;
                case "text":
                  html = widget.data.text;
                  items = [
                    {
                      xtype: "container",
                      margin: 4,
                      html: widget.data.text,
                      listeners: {
                        render: function(p){
                          console.log(p.getWidth());
                        },
                      },
                    },
                  ];
                  break;
              }
              panel.add({
                xtype: "panel",
                title: widget.title,
                cls: "noc-home-widget",
                border: true,
                // layout: "fit",
                style: {
                  borderRadius: "8px 8px 0 0",
                },
                bodyStyle: {
                  // padding: "4px",
                  borderRadius: "0 0 8px 8px",
                  backgroundColor: "#ecf0f1",
                  borderColor: "#ecf0f1 !important",
                },
                shrinkWrap: true,
                scrollable: true,
                // html: html,
                // items: items,
                listeners: {
                  render: function(p){
                    console.log(p.getWidth());
                  },
                },
              });
            }, this);
          }
        },
        failure: function(){
          NOC.error(__("Failed to get home data"));
        },
        callback: function(){
          panel.unmask();
        },
      });
    },
  },
});
