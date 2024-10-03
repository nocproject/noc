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
      text: __("Created"),
      dataIndex: "created_at",
      width: 250,
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
        glyph: NOC.glyph.refresh,
        tooltip: __("Refresh"),
        handler: "onRefresh",
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
        scrollable: true,
      },
      {
        itemId: "jobData",
        region: "east",
        width: 350,
        scrollable: "y",
        defaults: {
          padding: 4,
          allowBlank: true,
        },
        listeners: {
          resize: function(component){
            component.updateLayout();
          },
        },
        items: [
          {
            xtype: "displayfield",
            name: "status",
            fieldLabel: __("Status"),
            renderer: NOC.render.JobStatus,
          },
          {
            xtype: "displayfield",
            name: "name",
            fieldLabel: __("Name"),
          },
          {
            xtype: "displayfield",
            name: "description",
            fieldLabel: __("Description"),
          },
          {
            xtype: "grid",
            title: __("Inputs"),
            name: "inputs",
            visible: false,
            columns: [
              {text: __("Name"), dataIndex: "name", flex: 1},
              {text: __("Value"), dataIndex: "value", flex: 1},
            ],
            store: {
              fields: ["name", "value"],
              data: [
              ],
            },
          },
          {
            xtype: "grid",
            title: __("Environment"),
            name: "environment",
            visible: false,
            columns: [
              {text: __("Name"), dataIndex: "name", flex: 1},
              {text: __("Value"), dataIndex: "value", flex: 1},
            ],
            store: {
              fields: ["name", "value"],
              data: [
              ],
            },
          },
        ],
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
    me.setRightPanelValues(record);
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
        html: me.transformSvg(svg).outerHTML,
        listeners: {
          afterrender: function(){
            var svgElement = container.getEl().dom.querySelector("svg"),
              elements = svgElement.querySelectorAll(".job-selectable");

            elements.forEach(function(element){
              element.addEventListener("click", function(event){
                var record = me.grid.getStore().getById(element.id);

                event.stopPropagation();
                svgElement.querySelectorAll(".active-job").forEach(function(el){
                  el.classList.remove("active-job");
                });
                element.classList.add("active-job");
                if(Ext.isEmpty(record)){
                  me.sendRequest(element.id, function(response){
                    var data = Ext.decode(response.responseText);
                    me.setRightPanelValues(Ext.create('Ext.data.Record', data));
                  });
                } else{
                  me.setRightPanelValues(record);
                }
              });
            });
          },
        },
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

    me.sendRequest(parentId, function(response){
      var data = Ext.decode(response.responseText);
      me.onEditRecord(Ext.create('Ext.data.Record', data));
      me.setHistoryHash(parentId);
    });
  },
  //
  setRightPanelValues: function(record){
    var me = this,
      dataPanel = me.down("#jobData"),
      inputs = Ext.Array.map(record.get("inputs"), function(item){
        return {name: item.name, value: item.value}
      }),
      environment = Ext.Array.map(Ext.Object.getKeys(record.get("environment")), function(key){
        return {name: key, value: record.get("environment")[key]}
      });
    
    dataPanel.down("[name=status]").setValue(record.get("status"));
    dataPanel.down("[name=name]").setValue(record.get("name"));
    dataPanel.down("[name=description]").setValue(record.get("description"));
    if(inputs.length){
      dataPanel.down("[name=inputs]").show();
      dataPanel.down("[name=inputs]").getStore().loadData(inputs);
    } else{
      dataPanel.down("[name=inputs]").hide();
    }
    if(environment.length){
      dataPanel.down("[name=environment]").show();
      dataPanel.down("[name=environment]").getStore().loadData(environment);
    } else{
      dataPanel.down("[name=environment]").hide();
    }
  },
  //
  sendRequest: function(itemId, callBack){
    Ext.Ajax.request({
      url: "/sa/job/" + itemId + "/",
      method: "GET",
      success: callBack,
      failure: function(response){
        NOC.error(__("Failed to get data for job") + ": " + response.status);
      },
    });
  },
  //
  transformSvg: function(svg){
    var background = "white";
    svg.querySelector(".graph").classList.remove("job-selectable");
    svg.querySelectorAll(".node.job-selectable>polygon")
      .forEach(el => el.setAttribute("fill", background));
    svg.querySelectorAll(".cluster.job-selectable>path")
      .forEach(el => el.setAttribute("fill", background));
    svg.querySelectorAll("title").forEach(el => el.remove());
    return svg;
  },
  //
  onRefresh: function(){
    this.onEditRecord(this.currentRecord);
  },
});