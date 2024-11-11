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
    "NOC.inv.inv.plugins.Zoom",
  ],
  model: "NOC.sa.job.Model",
  defaultListenerScope: true,
  canAdd: false,
  xtype: "sajob",
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
        xtype: "invPluginsZoom",
        itemId: "zoomControl",
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
        xtype: "container",
        itemId: "schemeContainer",
        region: "center",
        layout: "fit",
        scrollable: true,
        style: {
          backgroundColor: "white",
        },
        listeners: {
          afterrender: "afterPanelsRender",
          click: {
            element: "el",
            fn: "onSchemeClick",
          },
        },
      },
      {
        itemId: "jobData",
        region: "east",
        width: 350,
        scrollable: "y",
        defaults: {
          padding: "0 4",
          margin: 0,
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
            name: "action",
            fieldLabel: __("Action"),
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

  afterPanelsRender: function(panel){
    var tabPanel = panel.up("tabpanel"),
      bodyHeight = tabPanel.body.getHeight(),
      dockedItemsHeight = this.getDockedItems().reduce(function(totalHeight, item){
        return totalHeight + item.getHeight();
      }, 0);
    panel.setHeight(bodyHeight - dockedItemsHeight);
  },

  onEditRecord: function(record){
    var me = this;
    
    me.currentRecord = record;
    me.showItem(me.ITEM_DETAIL);
    me.down("#goToParentBtn").setDisabled(Ext.isEmpty(record.get("parent")));
    me.setHistoryHash(record.id);
    me.setRightPanelValues(record);
    me.sendRequest(record.id, "/viz/", function(response){
      var data = Ext.decode(response.responseText);
      me.renderScheme(data);
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
      Ext.Loader.loadScript({
        url: "/ui/pkg/viz-js/viz-standalone.js",
        onLoad: function(){
          this._render(data);
        },
        scope: me,
      });
    } else{
      me._render(data);
    }
  },
  //
  _render: function(data){
    var me = this;

    Viz.instance().then(function(viz){ 
      var svg,
        container = me.down("[itemId=schemeContainer]"),
        svgData = viz.renderSVGElement(data),
        zoomControl = me.down("#zoomControl");
     
      svgData.setAttribute("height", "100%");
      svgData.setAttribute("width", "100%");
      svgData.setAttribute("preserveAspectRatio", "xMinYMin meet");
      svgData.setAttribute("object-fit", "contain");
      container.setHtml(me.transformSvg(svgData).outerHTML);
      svg = container.getEl().dom.querySelector("svg");
      svg.onwheel = Ext.bind(zoomControl.onWheel, zoomControl);
      zoomControl.reset();
    });
  },
  //
  onSchemeClick: function(event, target){
    var me = this,
      element = target.closest(".job-selectable");
    if(element){
      var record = me.grid.getStore().getById(element.id),
        svgElement = target.closest("svg");
      
      svgElement.querySelectorAll(".active-job").forEach(function(el){
        el.classList.remove("active-job");
      });
      element.classList.remove("job-selectable");
      element.classList.add("active-job");
      element.addEventListener("mouseleave", function(){
        element.classList.add("job-selectable");
      }, {once: true});
      if(Ext.isEmpty(record)){
        me.sendRequest(element.id, "/", function(response){
          var data = Ext.decode(response.responseText);
          me.setRightPanelValues(Ext.create("Ext.data.Record", data));
        });
      } else{
        me.setRightPanelValues(record);
      }
    }
  },
  //
  onDownloadSVG: function(){
    var me = this,
      imageContainer = me.down("#schemeContainer"),
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

    me.sendRequest(parentId, "/", function(response){
      var data = Ext.decode(response.responseText);
      me.onEditRecord(Ext.create("Ext.data.Record", data));
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
      environment = Ext.Array.map(Ext.Object.getKeys(record.get("effective_environment")), function(key){
        return {name: key, value: record.get("effective_environment")[key]}
      });
    
    dataPanel.down("[name=status]").setValue(record.get("status"));
    dataPanel.down("[name=name]").setValue(record.get("name"));
    dataPanel.down("[name=action]").setValue(record.get("action"));
    dataPanel.down("[name=description]").setValue(record.get("description"));
    if(Ext.isEmpty(record.get("action"))){
      dataPanel.down("[name=action]").hide();
    } else{
      dataPanel.down("[name=action]").show();
    }
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
  sendRequest: function(itemId, suffix, callBack){
    var url = itemId ? "/sa/job/" + itemId + suffix : "/sa/job/";

    Ext.Ajax.request({
      url: url,
      method: "GET",
      success: callBack,
      failure: function(response){
        NOC.error(__("Failed to get data for job") + ": " + response.status);
      },
    });
  },
  //
  transformSvg: function(svg){
    // ToDo remove this function, all logic should be in Viz config
    var background = "white",
      graphEl = svg.querySelector(".graph");
    graphEl.classList.remove("job-selectable");
    graphEl.classList.forEach(className => {
      if(className.startsWith("job-status")){
        graphEl.classList.remove(className);
      }
    });
    svg.querySelectorAll(".node.job-selectable>polygon")
      .forEach(el => el.setAttribute("fill", background));
    svg.querySelectorAll(".cluster.job-selectable>path")
      .forEach(el => el.setAttribute("fill", background));
    svg.querySelectorAll("title").forEach(el => el.remove());
    return svg;
  },
});