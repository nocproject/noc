//---------------------------------------------------------------------
// main.home application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.home.Application");

Ext.define("NOC.main.home.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.core.layout.Flex",
  ],
  items: [
    {
      xtype: "container",
      layout: {
        type: "flex",
        direction: "column",
        wrap: "wrap",
        gap: "20px",
      },
      padding: 10,
      scrollable: true,
      smallHeight: 90,
      normalHeight: 200,
      extraHeight: 310,
      doubleHeight: 420,
      cellWidth: 200,
      items: [],
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
                Ext.each(data.widgets, function(widget){
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
                      items = [
                        {
                          xtype: "container",
                          margin: 4,
                          html: html + "</ul>", 
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
                      items = [
                        {
                          xtype: "container",
                          margin: 4,
                          html: "<table style='width: 100%'>" + rows.join("") + "</table>",
                        },
                      ];    
                      break;
                    case "text":
                      items = [
                        {
                          xtype: "container",
                          margin: 4,
                          html: widget.data.text,
                        },
                      ];
                      break;
                  }
                  panel.add(
                    Ext.create("Ext.panel.Panel", {
                      title: widget.title,
                      border: true,
                      style: {
                        borderRadius: "8px 8px 0 0",
                      },
                      bodyStyle: {
                        borderRadius: "0 0 8px 8px",
                        backgroundColor: "#ecf0f1",
                        borderColor: "#ecf0f1 !important",
                      },
                      width: this.cellWidth,
                      height: this[widget.height + "Height"] || this.normalHeight,
                      scrollable: true,
                      items: items,
                    }),
                  );
                }, this);
              }
              panel.unmask();
            },
            failure: function(){
              panel.unmask();
              NOC.error(__("Failed to get home data"));
            },
          });
        },
      },
    },
  ],
});
