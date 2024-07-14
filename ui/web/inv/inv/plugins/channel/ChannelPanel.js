//---------------------------------------------------------------------
// inv.inv Channel Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.channel.ChannelPanel");

Ext.define("NOC.inv.inv.plugins.channel.ChannelPanel", {
  extend: "Ext.panel.Panel",
  title: __("Channels"),
  closable: false,
  defaultListenerScope: true,
  layout: {
    type: "vbox",
    align: "stretch",
  },
  tbar: [
    {
      xtype: "combobox",
      store: [
        [0.25, "25%"],
        [0.5, "50%"],
        [0.75, "75%"],
        [1.0, "100%"],
        [1.25, "125%"],
        [1.5, "150%"],
        [2.0, "200%"],
        [3.0, "300%"],
        [4.0, "400%"],
      ],
      width: 100,
      value: 1.0,
      valueField: "zoom",
      displayField: "label",
      listeners: {
        select: "onZoom",
      },    
    },
    {
      xtype: "button",
      text: __("Magic"),
      itemId: "adhoc",
      glyph: NOC.glyph.magic,
      handler: "onAddHoc",
    },
  ],
  items: [
    {
      xtype: "grid",
      scrollable: "y",
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Tech Domain"),
          dataIndex: "tech_domain",
          width: 150,
          renderer: NOC.render.Lookup("tech_domain"),
        },
        {
          text: __("Kind"),
          dataIndex: "kind",
          widht: 50,
        },
        {
          text: __("Topo"),
          dataIndex: "topology",
          width: 100,
        },
        {
          text: __("From"),
          dataIndex: "from_endpoint",
          flex: 1,
        },
        {
          text: __("To"),
          dataIndex: "to_endpoint",
          flex: 1,
        },
      ],
      listeners: {
        afterlayout: "afterGridRender",
        selectionchange: "onChangeSelection", 
      },
    },
    {
      xtype: "container",
      flex: 1,
      layout: "fit",
      scrollable: true,
      items: [
        {
          xtype: "image",
          itemId: "scheme",
          hidden: true,
          padding: 5,
        },
      ],
    },
  ],
  preview: function(data, objectId){
    var me = this,
      grid = me.down("grid");
    me.currentId = objectId;
    grid.getStore().loadData(data.records);
  },
  //
  _render: function(dot){
    var me = this,
      viz = new Viz();
    viz.renderSVGElement(dot).then(function(el){
      var imageComponent = me.down("[itemId=scheme]");
      imageComponent.setHidden(false);
      imageComponent.setSrc(me.svgToBase64(el.outerHTML));
    });
  },
  //
  renderScheme: function(dot){
    var me = this;
    if(typeof Viz === "undefined"){
      new_load_scripts([
        "https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js",
        "https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js",          
      ], me, Ext.bind(me._render, me, [dot]));
    } else{
      me._render(dot);
    }
  },
  //
  onZoom: function(combo){
    var me = this,
      imageComponent = me.down("#scheme");
    imageComponent.getEl().dom.style.transformOrigin = "0 0";
    imageComponent.getEl().dom.style.transform = "scale(" + combo.getValue() + ")";
  },
  //
  svgToBase64: function(svgString){
    var base64String = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgString)));
    return base64String;
  },
  //
  onAddHoc: function(){
    var me = this,
      url = "/inv/inv/" + me.currentId + "/plugin/channel/adhoc/"
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: me,
      success: function(response){
        var obj = Ext.decode(response.responseText);
        if(Ext.isEmpty(obj)){
          NOC.info(__("No ad-hoc channels available"));
        } else{
          var adHocWindow = Ext.create("Ext.window.Window", {
            title: __("Create Ad-Hoc channel"),
            height: 200,
            width: 600,
            layout: "fit",
            modal: true,
            items: [
              {
                xtype: "form",
                bodyPadding: 10,
                layout: "anchor",
                defaults: {
                  anchor: "100%",
                  labelWidth: 200,
                },
                items: [
                  {
                    xtype: "combobox",
                    fieldLabel: __("Select starting point"),
                    store: new Ext.data.Store({
                      fields: ["tracer", "object__label", "object"],
                      data: obj,
                    }),
                    queryMode: "local",
                    displayField: "object__label",
                    valueField: "object",
                    tpl: Ext.create("Ext.XTemplate",
                                    "<tpl for='.'>",
                                    "<div class='x-boundlist-item'>{tracer} {object__label}</div>",
                                    "</tpl>",
                    ),
                    listeners: {
                      change: function(combo, newValue){
                        adHocWindow.down("#createButton").setDisabled(!newValue);
                      },
                    },
                  },
                ],
                buttons: [
                  {
                    text: __("Create"),
                    itemId: "createButton",
                    disabled: true,
                    handler: function(){
                      var form = this.up("form"),
                        combo = form.down("combobox"),
                        selectedValue = combo.getValue(),
                        selectedRecord = combo.findRecordByValue(selectedValue);
                      console.log("Selected record", selectedRecord);
                      Ext.Ajax.request({
                        url: "/inv/inv/" + me.currentId + "/plugin/channel/adhoc/",
                        method: "POST",
                        jsonData: {object: selectedValue, tracer: selectedRecord.get("tracer")},
                        success: function(response){
                          var data = Ext.decode(response.responseText);
                          if(data.status){
                            NOC.info(data.msg);
                            adHocWindow.close();
                            NOC.launch("inv.channel", "history", {"args": [data.channel]})
                          } else{
                            NOC.error(data.msg);
                          }
                        },
                        failure: function(response){
                          console.log("Failure", response);
                        },
                      });
                    },
                  },
                  {
                    text: "Cancel",
                    handler: function(){
                      adHocWindow.close();
                    },
                  },
                ],
              },
            ],
          });
          adHocWindow.show();
        }
      },
      failure: function(response){
        NOC.error(__("Failed to get data") + ": " + response.status);
      },
    });
  },
  //
  onChangeSelection: function(grid, selected){
    if(selected.length > 0){
      var me = this,
        recordData = selected[0].getData(),
        url = "/inv/channel/" + recordData.id + "/dot/";
      Ext.Ajax.request({
        url: url,
        method: "GET",
        scope: me,
        success: function(response){
          var obj = Ext.decode(response.responseText);
          this.renderScheme(obj.dot);
        },
        failure: function(response){
          NOC.error(__("Failed to get data") + ": " + response.status);
        },
      });
    }
  },
  //
  afterGridRender: function(grid){
    var me = this,
      gridHeight = grid.getHeight(),
      containerHeight = me.up("tabpanel").body.getHeight();
    if(gridHeight > containerHeight / 2){
      grid.setHeight(containerHeight / 2);
    }
  },
});
