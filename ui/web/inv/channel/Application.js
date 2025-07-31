//---------------------------------------------------------------------
// inv.channel application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.channel.Application");

Ext.define("NOC.inv.channel.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.inv.channel.Model",
    "NOC.inv.channel.LookupField",
    "NOC.inv.channel.EndpointModel",
    "NOC.inv.inv.plugins.Zoom",
    "NOC.inv.techdomain.LookupField",
    "NOC.core.label.LabelField",
    "NOC.project.project.LookupField",
    "NOC.crm.subscriber.LookupField",
    "NOC.crm.supplier.LookupField",
    "NOC.main.remotesystem.LookupField",
    "NOC.inv.techdomain.LookupField",
    "Ext.ux.form.GridField",
  ],
  mixins: [
    "NOC.inv.inv.plugins.Mixins",
  ],
  model: "NOC.inv.channel.Model",
  xtype: "invchannel",
  search: true,
  initComponent: function(){
    var me = this;

    me.mapPanel = Ext.create("Ext.panel.Panel", {
      app: me,
      title: __("Map"),
      layout: "fit",
      items: [
        {
          xtype: "container",
          flex: 1,
          layout: "fit",
          scrollable: true,
          itemId: "schemeContainer",
          listeners: {
            click: {
              element: "el",
              scope: me,
              fn: me.onSchemeClick,
            },
          },
        },
      ],
      tbar: [
        {
          text: __("Close"),
          glyph: NOC.glyph.arrow_left,
          scope: me,
          handler: "onCloseMap",
        },
        {
          xtype: "invPluginsZoom",
          itemId: "zoomControl",
        },
      ],
    });
    me.ITEM_MAP = me.registerItem(me.mapPanel);
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Parent"),
          dataIndex: "parent",
          width: 200,
          renderer: NOC.render.Lookup("parent"),
        },
        {
          text: __("Tech Domain"),
          dataIndex: "tech_domain",
          width: 200,
          renderer: NOC.render.Lookup("tech_domain"),
        },
        {
          text: __("Project"),
          dataIndex: "project",
          width: 200,
          renderer: NOC.render.Lookup("project"),
        },
        {
          text: __("Subscriber"),
          dataIndex: "subscriber",
          width: 200,
          renderer: NOC.render.Lookup("subscriber"),
        },
        {
          text: __("Supplier"),
          dataIndex: "supplier",
          width: 200,
          renderer: NOC.render.Lookup("supplier"),
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "medium",
          autoFocus: true,
        },
        {
          name: "parent",
          xtype: "inv.channel.LookupField",
          fieldLabel: __("Parent"),
          uiStyle: "medium",
          allowBlank: true,
        },
        {
          name: "tech_domain",
          xtype: "inv.techdomain.LookupField",
          fieldLabel: __("Tech Domain"),
          uiStyle: "medium",
          allowBlank: false,
        },
        {
          name: "controller",
          xtype: "textfield",
          fieldLabel: __("Controller"),
          uiStyle: "medium",
          allowBlank: true,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "discriminator",
          xtype: "textfield",
          fieldLabel: __("Discriminator"),
          allowBlank: true,
          uiStyle: "medium",
        },
        {
          name: "project",
          xtype: "project.project.LookupField",
          fieldLabel: __("Project"),
          allowBlank: true,
        },
        {
          name: "supplier",
          xtype: "crm.supplier.LookupField",
          fieldLabel: __("Supplier"),
          allowBlank: true,
        },
        {
          name: "subscriber",
          xtype: "crm.subscriber.LookupField",
          fieldLabel: __("Subscriber"),
          allowBlank: true,
        },
        {
          name: "labels",
          fieldLabel: __("Labels"),
          xtype: "labelfield",
          allowBlank: true,
          minWidth: 100,
          query: {
            allow_models: ["inv.Channel"],
          },
        },
        {
          name: "constraints",
          fieldLabel: __("Constraints"),
          xtype: "gridfield",
          columns: [
            {
              text: __("Type"),
              dataIndex: "type",
              width: 100,
              renderer: function(v){
                if(v === "i"){
                  return __("Include");
                }
                if(v === "e"){
                  return __("Exclude");
                }
                return "-";
              },
              editor: {
                xtype: "combobox",
                minWidth: 200,
                store: [
                  ["i", __("Include")],
                  ["e", __("Exclude")],
                ],
              },
            },
            {
              text: __("Strict"),
              dataIndex: "strict",
              width: 50,
              renderer: NOC.render.Bool,
              editor: "checkbox",
            },
            {
              text: __("Resource"),
              dataIndex: "resource",
              flex: 1,
              editor: "textfield",
            },
          ],
        },
        {
          name: "params",
          fieldLabel: __("Params"),
          xtype: "gridfield",
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              width: 100,
            },
            {
              text: __("Value"),
              dataIndex: "value",
              flex: 1,
            },
          ],
        },
        /*
        {
          name: "effective_labels",
          xtype: "labeldisplay",
          fieldLabel: __("Effective Labels"),
          allowBlank: true,
        },
        */
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Integration"),
          defaults: {
            padding: 4,
            labelAlign: "top",
          },
          items: [
            {
              name: "remote_system",
              xtype: "main.remotesystem.LookupField",
              fieldLabel: __("Remote System"),
              allowBlank: true,
            },
            {
              name: "remote_id",
              xtype: "textfield",
              fieldLabel: __("Remote ID"),
              allowBlank: true,
              uiStyle: "medium",
            },
            {
              name: "bi_id",
              xtype: "displayfield",
              fieldLabel: __("BI ID"),
              allowBlank: true,
              uiStyle: "medium",
            },
          ],
        },
      ],
      inlines: [
        {
          title: __("Endpoints"),
          model: "NOC.inv.channel.EndpointModel",
          columns: [
            {
              text: __("Resource"),
              dataIndex: "resource",
              width: 200,
              editor: "textfield",
              renderer: NOC.render.Lookup("resource"),
            },
            {
              text: __("Is Root"),
              dataIndex: "is_root",
              width: 50,
              renderer: NOC.render.Bool,
              editor: "checkbox",
            },
            {
              text: __("Pair"),
              dataIndex: "pair",
              width: 50,
              editor: {
                xtype: "numberfield",
                minWidth: 100,
              },
            },
            {
              text: __("Used by"),
              dataIndex: "used_by",
              flex: 1,
              renderer: function(v){
                return v.map(function(x){
                  if(x.discriminator === ""){
                    return x.channel__label;
                  } else{
                    return x.channel__label + " [" + x.discriminator + "]";
                  }
                }).join(", ");
              },
            },
            {
              text: __("Constraints"),
              dataIndex: "constraints",
              flex: 1,
              renderer: function(v){
                return v.map(function(x){
                  return x.name + " = [" + x.values.join(", ") + "]"
                }).join("; ");
              },
            },
          ],
        },
      ],
      formToolbar: [
        {
          text: __("Map"),
          glyph: NOC.glyph.globe,
          tooltip: __("Show Map"),
          scope: me,
          handler: me.onMap,
        },
      ],
    });
    me.callParent();
  },
  //
  filters: [
    {
      title: __("By Tech Domai"),
      name: "tech_domain",
      ftype: "lookup",
      lookup: "inv.techdomain",
    },
    {
      title: __("By Project"),
      name: "project",
      ftype: "lookup",
      lookup: "project.project",
    },
    {
      title: __("By Supplier"),
      name: "supplier",
      ftype: "lookup",
      lookup: "crm.supplier",
    },
    {
      title: __("By Subscriber"),
      name: "subscriber",
      ftype: "lookup",
      lookup: "crm.subscriber",
    },
  ],
  //
  onMap: function(){
    var me = this,
      currentId = me.currentRecord.id,
      url = `/inv/channel/${currentId}/viz/`;
    Ext.Ajax.request({
      url: url,
      method: "GET",
      success: function(response){
        var obj = Ext.decode(response.responseText);
        me.renderScheme(obj.data);
        me.showItem(me.ITEM_MAP);
      },
      failure: function(response){
        NOC.error("Error status: " + response.status);
      },
    });
  },
  //
  onCloseMap: function(){
    var me = this;
    me.showForm();
  },
  //
  svgToBase64: function(svgString){
    var base64String = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgString)));
    return base64String;
  },
  //
  _render: function(data){
    var me = this;
    Viz.instance().then(function(viz){ 
      var svg, container = me.down("[itemId=schemeContainer]"),
        svgData = viz.renderSVGElement(data),
        zoomControl = me.down("#zoomControl");
      svgData.setAttribute("height", "100%");
      svgData.setAttribute("width", "100%");
      svgData.setAttribute("preserveAspectRatio", "xMinYMin meet");
      svgData.setAttribute("object-fit", "contain");
      container.setHtml(svgData.outerHTML);
      svg = container.getEl().dom.querySelector("svg");
      svg.onwheel = Ext.bind(zoomControl.onWheel, zoomControl);
      zoomControl.reset();

    });
  },
  //
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
  onSchemeClick: function(event, target){
    let channelEl = target.closest(".ch-selectable");
    if(Ext.isEmpty(channelEl)){
      return;
    }
    if(channelEl.id && channelEl.id.startsWith("click:")){
      let [, action, resource] = channelEl.id.split(":"),
        resourceData = decodeURIComponent(resource);
      if(action === "info"){
        this.showBalloon(this, "schemeBalloon", resourceData, [event.pageX, event.pageY]);
      }
    }
  },
});
