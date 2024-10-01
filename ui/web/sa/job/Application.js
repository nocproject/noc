//---------------------------------------------------------------------
// sa.job application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.job.Application");

Ext.define("NOC.sa.job.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.sa.job.Model",
  ],
  model: "NOC.sa.job.Model",
  defaultListenerScope: true,
  canAdd: false,
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      width: 200,
    },
    {
      text: __("Description"),
      dataIndex: "description",
      flex: 1,
    },
    {
      text: __("Action"),
      dataIndex: "action",
      width: 100,
    },
    {
      text: __("Status"),
      dataIndex: "status",
      width: 150,
      renderer: NOC.render.JobStatus,
    },
  ],
  detail: {
    xtype: "panel",
    title: __("Job Details"),
    layout: "border",
    tbar: [
      {
        text: __("Close"),
        glyph: NOC.glyph.arrow_left,
        handler: "onCloseDetail",
      },
      {
        glyph: NOC.glyph.arrow_up,
        itemId: "goToParentBtn",
        tooltip: __("Go to Parent"),
        disabled: true,
        handler: "onGoToParent",
      },
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
        editable: false,
        listeners: {
          select: "onZoom",
        },    
      },
      {
        xtype: "button",
        itemId: "downloadSVGBtn",
        tooltip: __("Download image as SVG"),
        glyph: NOC.glyph.download,
        handler: "onDownloadSVG",
      },

    ],
    defaults: {
      xtype: "panel",
      border: true,
      split: true,
    },
    items: [
      {
        itemId: "jobScheme",
        region: "center",
      },
      {
        region: "east",
        width: 250,
      },
    ],
  },
  initComponent: function(){
    var me = this,
      details = Ext.create(Ext.apply(me.detail, {app: me}));

    me.callParent();
    me.ITEM_DETAIL = me.registerItem(details);
    me.add(details);
    me.getLayout().setActiveItem(0);
  },

  onEditRecord: function(record){
    var me = this,
      url = "/sa/job/" + record.id + "/viz/";
    
    me.currentRecord = record;
    me.showItem(me.ITEM_DETAIL);
    me.down("#goToParentBtn").setDisabled(Ext.isEmpty(record.get("parent")));
    me.setHistoryHash(record.id);
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        this.renderScheme(data);
      },
      failure: function(response){
        NOC.error(__("Failed to get data") + ": " + response.status);
      },
    });
  },

  onCloseDetail: function(){
    this.showGrid();
    if(Ext.Object.isEmpty(this.currentQuery)){
      return;
    }
    // case restore by id
    this.currentQuery = undefined;
    this.reloadStore();
  },

  renderScheme: function(data){
    var me = this;

    if(typeof Viz === "undefined"){
      new_load_scripts([
        "/ui/pkg/viz-js/viz-standalone.js",
      ], me, Ext.bind(me._render, me, [data]));
    } else{
      me._render(data);
    }
  },
  //
  _render: function(data){
    var me = this;

    Viz.instance().then(function(viz){ 
      var container = me.down("[itemId=jobScheme]"),
        svg = viz.renderSVGElement(data);
      
      container.removeAll();
      container.add({
        xtype: "container",
        html: svg.outerHTML,
      });
    });
  },
  //
  onZoom: function(combo){
    var me = this,
      imageComponent = me.down("#jobScheme container");
    
    imageComponent.getEl().dom.style.transformOrigin = "0 0";
    imageComponent.getEl().dom.style.transform = "scale(" + combo.getValue() + ")";
  },
  //
  onDownloadSVG: function(){
    var me = this,
      imageContainer = me.down("#jobScheme container"),
      image = imageContainer.getEl().dom.querySelector("svg"),
      svgData = new XMLSerializer().serializeToString(image),
      blob = new Blob([svgData], {type: "image/svg+xml"}),
      url = URL.createObjectURL(blob),
      a = document.createElement("a");

    a.href = url;
    a.download = `job-scheme-${me.currentRecord.id}.svg`;
    a.click();
  },
  //
  onGoToParent: function(){
    var me = this,
      parentId = me.currentRecord.get("parent");

    Ext.Ajax.request({
      url: "/sa/job/" + parentId + "/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        this.onEditRecord(Ext.create('Ext.data.Record', data));
        me.setHistoryHash(parentId);
      },
      failure: function(response){
        NOC.error(__("Failed to get data for job") + ": " + response.status);
      },
    });
  },
});