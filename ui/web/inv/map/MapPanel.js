//---------------------------------------------------------------------
// Network Map Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2026 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.MapPanel");

Ext.define("NOC.inv.map.MapPanel", {
  extend: "Ext.panel.Panel",
  requires: ["NOC.inv.map.ShapeRegistry", "NOC.inv.map.MapRenderer"],
  layout: "fit",
  scrollable: true,
  app: null,
  readOnly: false,
  pollingInterval: 180000,
  updatedPollingTaskId: null,
  CAP_STP: "Network | STP",

  // Link overlay modes
  LO_NONE: 0,
  LO_LOAD: 1,

  resizeHandles: "onResize",

  initComponent: function(){
    var me = this;

    me.shapeRegistry = NOC.inv.map.ShapeRegistry;
    me.renderer = Ext.create("NOC.inv.map.MapRenderer", me);
    me.usedImages = {};
    me.hasStp = false;
    me.objectNodes = {};
    me.objectsList = [];
    me.portObjects = {}; // port id -> object id
    me.currentStpRoots = {};
    me.currentStpBlocked = {};
    me.linkBw = {}; // Link id -> {in: ..., out: ...}
    me.isInteractive = false; // Graph is editable
    me.isDirty = false; // Graph is changed
    me.statusPollingTaskId = null;
    me.overlayPollingTaskId = null;
    me.currentHighlight = null;
    me.overlayMode = me.LO_NONE;
    me.interfaceMetrics = [];

    Ext.apply(me, {
      items: [
        {
          xtype: "component",
          autoScroll: true,
          layout: "fit",
        },
      ],
    });
    //
    me.nodeMenu = Ext.create("Ext.menu.Menu", {
      items: [
        {
          text: __("Topology Neighbors"),
          glyph: NOC.glyph.map_o,
          scope: me,
          handler: me.onNodeMenuViewMap,
          menuOn: ["managedobject"],
        },
        {
          text: __("View Card"),
          glyph: NOC.glyph.eye,
          scope: me,
          handler: me.onNodeMenuViewCard,
          menuOn: ["managedobject"],
        },
        {
          text: __("Object Settings"),
          glyph: NOC.glyph.pencil,
          scope: me,
          handler: me.onNodeMenuEdit,
          menuOn: ["managedobject"],
        },
        {
          text: __("Show dashboard"),
          glyph: NOC.glyph.line_chart,
          scope: me,
          handler: me.onNodeMenuDashboard,
          menuOn: ["managedobject", "link"],
        },
        {
          text: __("To maintaince mode"),
          glyph: NOC.glyph.plus,
          scope: me,
          handler: me.onNodeMenuMaintainceMode,
          menuOn: "managedobject",
        },
        {
          text: __("Create new maintaince"),
          glyph: NOC.glyph.wrench,
          scope: me,
          handler: me.onNodeMenuNewMaintaince,
          menuOn: "managedobject",
        },
        {
          text: __("Add to group"),
          glyph: NOC.glyph.shopping_basket,
          scope: me,
          handler: me.onNodeMenuAddToBasket,
          menuOn: "managedobject",
        },
      ],
    });
    me.segmentMenu = Ext.create("Ext.menu.Menu", {
      items: [
        {
          text: __("Add all objects to group"),
          glyph: NOC.glyph.shopping_basket,
          scope: me,
          handler: me.onSegmentMenuAddToBasket,
          menuOn: ["managedobject", "link"],
        },
      ],
    });
    me.nodeMenuObject = null;
    me.nodeMenuObjectType = null;
    me.tip = Ext.create("Ext.tip.ToolTip", {
      dismissDelay: 0,
      saveDelay: 0,
      // showDelay: 0,
      // hideDelay: 100,
      closable: true,
      autoShow: false,
      tpl: new Ext.XTemplate(
        "<table style='font-size: 10px'>",
        "<tpl for='.'>",
        "<tr><td>{values}</td><td>|</td><td>Load {names} Mb</td><td>|</td><td>{port}</td></tr>",
        "</tpl>",
        "</table>",
      ),
    });
    //
    me.callParent();
  },

  afterRender: function(){
    var me = this;
    me.callParent();
    me.initMap();
    this.boundScrollHandler = Ext.bind(this.moveViewPort, this);
    this.body.dom.addEventListener("scroll", this.boundScrollHandler);
  },
  destroy: function(){
    var dom = this.body.dom;
    if(this.boundScrollHandler){
      dom.removeEventListener("scroll", this.boundScrollHandler);
    }
    if(this.rafId){
      cancelAnimationFrame(this.rafId);
    }
    this.callParent();
  },
  // ViewPort
  inThrottle: false,
  rafId: null,
  setViewPortSize: function(){
    var {width, height} = this.body.el.dom.getBoundingClientRect(),
      {sx, sy} = this.paper.scale();
    if(this.viewPort){
      this.viewPort.size(width / sx, height / sy);
    }
  },
  //
  moveViewPort: function(evt){
    if(!this.inThrottle){
      this.inThrottle = true;
      this.rafId = requestAnimationFrame(() => {
        this.handleViewPortScroll(evt);
        this.inThrottle = false;
      });
    }
  },
  //
  handleViewPortScroll: function(evt){
    var {scrollLeft, scrollTop} = evt.target,
      {sx, sy} = this.paper.scale(),
      // {x, y} = this.paper.clientToLocalPoint({x: scrollLeft, y: scrollTop}),
      moveX = Math.trunc(scrollLeft / sx),
      moveY = Math.trunc(scrollTop / sy);

    if(this.viewPort){
      this.viewPort.position(moveX, moveY);
      // this.viewPort.position(x, y);
    }
  },
  // Initialize JointJS Map
  initMap: function(){
    var me = this,
      dom = me.items.first().el.dom;
    me.graph = new joint.dia.Graph();
    me.graph.on("change", Ext.bind(me.onChange, me));
    me.paper = new joint.dia.Paper({
      el: dom,
      model: me.graph,
      preventContextMenu: false,
      async: false,
      guard: function(evt){
        return evt.type === "mousedown" && evt.buttons === 2;
      },
      interactive: Ext.bind(me.onInteractive, me),
    });
    // Apply SVG filters
    me.renderer.initFilters();
    // Subscribe to events
    me.paper.on("cell:pointerdown", Ext.bind(me.onCellSelected, me));
    me.paper.on("cell:pointerdblclick", Ext.bind(me.onCellDoubleClick, me));
    me.paper.on("blank:pointerdown", Ext.bind(me.onBlankSelected, me));
    me.paper.on("cell:highlight", Ext.bind(me.onCellHighlight, me));
    me.paper.on("cell:unhighlight", Ext.bind(me.onCellUnhighlight, me));
    me.paper.on("cell:contextmenu", Ext.bind(me.onContextMenu, me));
    me.paper.on("blank:contextmenu", Ext.bind(me.onSegmentContextMenu, me));
    me.paper.on("link:mouseenter", Ext.bind(me.onLinkOver, me));
    me.paper.on("link:mouseleave", Ext.bind(me.onLinkOut, me));
    me.fireEvent("mapready");
  },
  // Load segment data
  loadSegment: function(generator, segmentId, forceSpring){
    var me = this,
      url;
    me.generator = generator || "segment";
    url = "/inv/map/" + me.generator + "/" + segmentId + "/data/";
    if(forceSpring){
      url += "?force=spring";
    }
    me.segmentId = segmentId;
    me.mask(__("Map loading ..."));
    Ext.Ajax.request({
      url: url,
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.error){
          NOC.error(data.error);
        } else{
          me.renderMap(data);
        }
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
      callback: function(){
        me.unmask();
      },
    });
  },
  //
  renderMap: function(data){
    var me = this;
    me.renderer.renderMap(data);
  },
  //
  unhighlight: function(){
    var me = this;
    if(me.currentHighlight){
      me.currentHighlight.unhighlight();
      me.currentHighlight = null;
    }
    me.nodeMenu.hide();
  },
  //
  onCellSelected: function(view){
    var me = this,
      data = view.model.get("data");
    this.unhighlight();
    if(Ext.isEmpty(data)){
      this.onBlankSelected();
      return;
    }
    switch(data.type){
      case "managedobject":
        view.highlight();
        me.currentHighlight = view;
        me.app.inspectManagedObject(data.id);
        break;
      case "link":
        me.app.inspectLink(data.id);
        break;
      case "cloud":
        view.highlight();
        me.currentHighlight = view;
        me.app.inspectCloud(data.id);
        break;
      case "objectgroup":
        view.highlight();
        me.currentHighlight = view;
        me.app.inspectObjectGroup(data.node_id);
        break;
      case "objectsegment":
        view.highlight();
        me.currentHighlight = view;
        me.app.inspectObjectSegment(data.node_id);
        break;
      case "cpe":
        view.highlight();
        me.currentHighlight = view;
        me.app.inspectCPE(data.node_id);
        break;
      case "other":
        view.highlight();
        me.currentHighlight = view;
        me.app.inspectObjectPortal(data.portal);
        break;
    }
  },

  onSegmentContextMenu: function(evt){
    var me = this;
    evt.preventDefault();
    me.segmentMenu.showAt(evt.clientX, evt.clientY);
  },

  onLinkOver: function(link, evt){
    var me = this,
      data,
      rows = [],
      nameByPort = function(portId){
        var elementNameAttr = "name";
        if(me.app.addressIPButton.pressed){
          elementNameAttr = "address";
        }
        if(link.model.getTargetElement().get("data").id === me.portObjects[portId]){
          return link.model.getTargetElement().get(elementNameAttr);
        }
        if(link.model.getSourceElement().get("data").id === me.portObjects[portId]){
          return link.model.getSourceElement().get(elementNameAttr);
        }
      };
    // prevent bounce
    me.popupOffsetX = evt.offsetX;
    me.popupOffsetY = evt.offsetY;
    if(me.overlayMode === me.LO_LOAD && me.tip.isHidden()){
      data = link.model.get("data");
      Ext.each(data.metrics, function(metric){
        var names = [],
          values = [];
        Ext.each(metric.metrics, function(dat){
          values.push(dat.value !== "-" ? (dat.value / 1024 / 1024).toFixed(2) : "-");
          names.push(dat.metric === "Interface | Load | Out" ? "Out" : "In");
        });
        rows.push({
          values: values.join(" / "),
          names: names.join(" / "),
          port: nameByPort(metric.port),
        });
      });
      if(rows.length){
        me.tip.setData(rows);
        me.tip.showAt([evt.pageX, evt.pageY]);
      }
    }
  },

  onLinkOut: function(link, evt){
    var me = this;
    // prevent bounce
    if(me.popupOffsetX !== evt.offsetX && me.popupOffsetY !== evt.offsetY){
      me.tip.hide();
    }
  },

  onContextMenu: function(view, evt){
    evt.preventDefault();
    var data = view.model.get("data");
    if(Ext.isEmpty(data)){
      this.onSegmentContextMenu(evt);
      return;
    }
    this.nodeMenuObject = view.model.get("id").split(":")[1];
    this.nodeMenuObjectType = data.type;
    if("wrench" !== this.nodeMenuObjectType){
      Ext.each(this.nodeMenu.items.items, function(item){
        item.setVisible(item.menuOn.indexOf(this.nodeMenuObjectType) !== -1);
      }, this);
      this.nodeMenu.showAt(evt.clientX, evt.clientY);
    }
  },
  //
  onCellDoubleClick: function(view){
    var data = view.model.get("data");
    if(Ext.isEmpty(data)) return;
    if(data.type === "managedobject"){
      window.open("/api/card/view/managedobject/" + data.id + "/");
    }
  },
  //
  onBlankSelected: function(){
    var me = this;
    me.unhighlight();
    me.app.inspectSegment();
  },
  // Change interactive flag
  setInteractive: function(interactive){
    var me = this;
    me.isInteractive = interactive;
  },
  //
  onInteractive: function(){
    var me = this;
    return me.isInteractive;
  },
  //
  onChange: function(){
    var me = this;
    me.isDirty = true;
    me.fireEvent("changed");
  },
  //
  onRotate: function(){
    var me = this,
      bbox = me.paper.getContentBBox();
    Ext.each(me.graph.getElements(), function(e){
      var pos = e.get("position");
      e.set("position", {
        x: -pos.y + bbox.height,
        y: pos.x,
      });
    });
    me.renderer.setPaperDimension();
  },
  //
  save: function(){
    var me = this,
      r = {
        nodes: [],
        links: [],
      };
    if(me.isConfiguredMap){
      var bbox = me.paper.getContentBBox();
      r.width = bbox.width - bbox.x;
      r.height = bbox.height - bbox.y;
    }
    // Get nodes position
    Ext.each(me.graph.getElements(), function(e){
      var data = e.get("data");
      if(!Ext.isEmpty(data) && !["wrench", "badge"].includes(data.type)){
        var v = e.get("id").split(":");
        r.nodes.push({
          type: v[0],
          id: v[1],
          x: e.get("position").x,
          y: e.get("position").y,
        });
      }
    });
    // Get links position
    Ext.each(me.graph.getLinks(), function(e){
      var vertices = e.get("vertices"),
        v = e.get("id").split(":"),
        lr = {
          type: v[0],
          id: v[1],
          connector: e.get("connector").name,
        };
      if(vertices){
        lr.vertices = vertices.map(function(o){
          return {
            x: o.x,
            y: o.y,
          };
        });
      }
      r.links.push(lr);
    });
    Ext.Ajax.request({
      url: "/inv/map/" + me.generator + "/" + me.segmentId + "/data/",
      method: "POST",
      jsonData: r,
      scope: me,
      success: function(){
        NOC.info(__("Map has been saved"));
        me.isDirty = false;
        me.app.saveButton.setDisabled(true);
      },
      failure: function(){
        NOC.error(__("Failed to save data"));
      },
    });
  },

  getObjectStatus: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/map/objects_statuses/",
      method: "POST",
      jsonData: {
        nodes: me.objectsList,
      },
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        me.startUpdatedTimer();
        me.renderer.applyObjectStatuses(data);
      },
      failure: function(){
        NOC.error(__("Objects statuses failure!"));
      },
    });
  },

  startUpdatedTimer: function(){
    var me = this,
      interval = 5;

    if(me.updatedPollingTaskId){
      Ext.TaskManager.stop(me.updatedPollingTaskId);
      me.updatedPollingTaskId = null;
    }

    me.updatedPollingTaskId = Ext.TaskManager.start({
      run: function(counter){
        var text = (counter - 1) * interval + " " + __("sec");
        this.fireEvent("updateTick", text);
      },
      interval: interval * 1000,
      onError: function(){
        console.error("Updated Polling Task!");
      },
      scope: me,
    });
  },

  getOverlayData: function(){
    var me = this;
    switch(me.overlayMode){
      case me.LO_LOAD:
        var r = [];
        Ext.each(me.interfaceMetrics, function(m){
          r.push({
            id: m.id,
            metric: "Interface | Load | In",
            tags: m.tags,
          });
          r.push({
            id: m.id,
            metric: "Interface | Load | Out",
            tags: m.tags,
          });
        });
        Ext.Ajax.request({
          url: "/inv/map/metrics/",
          method: "POST",
          jsonData: {
            metrics: r,
          },
          scope: me,
          success: function(response){
            me.renderer.setLoadOverlayData(Ext.decode(response.responseText));
          },
          failure: Ext.emptyFn,
        });
        break;
    }
  },

  stopPolling: function(){
    var me = this;
    if(me.statusPollingTaskId){
      Ext.TaskManager.stop(me.statusPollingTaskId);
      me.statusPollingTaskId = null;
    }
    if(me.overlayPollingTaskId){
      Ext.TaskManager.stop(me.overlayPollingTaskId);
      me.overlayPollingTaskId = null;
    }
  },

  setOverlayMode: function(mode){
    var me = this;
    // Stop polling when necessary
    if(mode === me.LO_NONE && me.overlayPollingTaskId){
      Ext.TaskManager.stop(me.overlayPollingTaskId);
      me.overlayPollingTaskId = null;
    }
    me.overlayMode = mode;
    // Start polling when necessary
    if(mode !== me.LO_NONE && !me.overlayPollingTaskId){
      me.overlayPollingTaskId = Ext.TaskManager.start({
        run: me.getOverlayData,
        interval: me.pollingInterval,
        scope: me,
      });
    }
    //
    if(mode === me.LO_NONE){
      me.renderer.resetOverlayData();
    } else{
      me.getOverlayData();
    }
  },

  // Display links load
  // data is dict of
  // metric -> {ts: .., value: }

  onCellHighlight: function(view, el){
    var me = this;
    V(el).attr("filter", "url(#highlight)");
    me.fireEvent("onSelectCell", view.model.get("data").id);
  },

  onCellUnhighlight: function(view, el){
    var me = this;
    V(el).attr("filter", "");
    me.fireEvent("onUnselectCell", null);
  },

  resetLayout: function(forceSpring){
    var me = this;
    if(!me.segmentId || !me.generator){
      return;
    }
    forceSpring = forceSpring || false;
    Ext.Ajax.request({
      url: "/inv/map/" + me.generator + "/" + me.segmentId + "/data/",
      method: "DELETE",
      scope: me,
      success: function(){
        me.loadSegment(me.generator, me.segmentId, forceSpring);
      },
      failure: function(){
        NOC.error(__("Failed to reset layout"));
      },
    });
  },

  setZoom: function(zoom){
    var me = this;
    me.renderer.setZoom(zoom);
  },
  
  onNodeMenuViewMap: function(){
    NOC.launch("inv.map", "history", {
      args: ["objectlevelneighbor", this.nodeMenuObject, this.nodeMenuObject ],
    });
  },

  onNodeMenuViewCard: function(){
    var me = this;
    window.open("/api/card/view/managedobject/" + me.nodeMenuObject + "/");
  },

  onNodeMenuEdit: function(){
    var me = this;
    NOC.launch("sa.managedobject", "history", {args: [me.nodeMenuObject]});
  },

  onNodeMenuDashboard: function(){
    var me = this,
      objectType = me.nodeMenuObjectType;

    if("managedobject" === me.nodeMenuObjectType) objectType = "mo";
    window.open(
      "/ui/grafana/dashboard/script/noc.js?dashboard=" +
        objectType +
        "&id=" +
        me.nodeMenuObject,
    );
  },

  onNodeMenuMaintainceMode: function(){
    var me = this,
      objectId = Number(me.nodeMenuObject);

    NOC.run("NOC.inv.map.Maintenance", __("Add To Maintenance"), {
      args: [
        {mode: "Object"},
        [
          {
            object: objectId,
            object__label: me.objectNodes[objectId].attributes.attrs.text.text,
          },
        ],
      ],
    });
  },

  addToMaintaince: function(objects){
    var elements = [];
    Ext.Array.forEach(objects, function(item){
      elements.push({
        object: item.get("object"),
        object__label: item.get("object__label"),
      });
    });
    NOC.run("NOC.inv.map.Maintenance", __("Add To Maintenance"), {
      args: [{mode: "Object"}, elements],
    });
  },

  newMaintaince: function(objects){
    var args = {
      direct_objects: objects,
      subject: __("created from map at ") + Ext.Date.format(new Date(), "d.m.Y H:i P"),
      contacts: NOC.email ? NOC.email : NOC.username,
      start_date: Ext.Date.format(new Date(), "d.m.Y"),
      start_time: Ext.Date.format(new Date(), "H:i"),
      stop_time: "12:00",
      suppress_alarms: true,
    };

    Ext.create("NOC.maintenance.maintenancetype.LookupField")
      .getStore()
      .load({
        params: {__query: "РНР"},
        callback: function(records){
          if(records.length > 0){
            Ext.apply(args, {
              type: records[0].id,
            });
          }
          NOC.launch("maintenance.maintenance", "new", {
            args: args,
          });
        },
      });
  },

  onNodeMenuNewMaintaince: function(){
    var me = this,
      objectId = Number(me.nodeMenuObject);
    me.newMaintaince([
      {
        object: objectId,
        object__label: me.objectNodes[objectId].attributes.attrs.text.text,
      },
    ]);
  },

  onNodeMenuAddToBasket: function(){
    var me = this,
      objectId = Number(me.nodeMenuObject);
    var store = Ext.data.StoreManager.lookup("basketStore");

    if(store.getCount() === 0){
      me.fireEvent("openbasket");
    }
    me.addObjectToBasket(objectId, store);
  },

  onSegmentMenuAddToBasket: function(){
    var me = this;
    var store = Ext.data.StoreManager.lookup("basketStore");

    if(store.getCount() === 0){
      me.fireEvent("openbasket");
    }
    Ext.each(this.graph.getElements(), function(e){
      if("managedobject" === e.get("id").split(":")[0]){
        var objectId = Number(e.get("id").split(":")[1]);
        me.addObjectToBasket(objectId, store);
      }
    });
  },

  addObjectToBasket: function(id, store){
    Ext.Ajax.request({
      url: "/sa/managedobject/" + id + "/",
      method: "GET",
      success: function(response){
        var data = Ext.decode(response.responseText);
        var object = {
          id: id,
          object: id,
          object__label: data.name,
          address: data.address,
          platform: data.platform__label,
          time: data.time_pattern,
        };
        store.add(object);
      },
      failure: function(){
        NOC.msg.failed(__("Failed to get object data"));
      },
    });
  },

  setStp: function(status){
    var me = this;
    if(status){
      me.pollStp();
    }
  },

  pollStp: function(){
    var me = this,
      stpNodes = [];
    // Get STP nodes
    Ext.Object.each(me.objectNodes, function(k, v){
      if(v.attributes.data?.caps?.indexOf(me.CAP_STP) !== -1){
        stpNodes.push(k);
      }
    });
    // Get STP status
    Ext.Ajax.request({
      url: "/inv/map/stp/status/",
      method: "POST",
      jsonData: {
        objects: stpNodes,
      },
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        me.setStpBlocked(data.blocked);
        me.setStpRoots(data.roots);
      },
      failure: function(){
        NOC.msg.failed(__("Failed to get STP status"));
      },
    });
  },

  setStpRoots: function(roots){
    var me = this,
      newStpRoots = {};
    // Set new STP roots
    Ext.each(roots, function(rootId){
      var root = me.objectNodes[rootId];
      if(root){
        if(!me.currentStpRoots[rootId]){
          me.objectNodes[rootId].attr("text/class", "stp-root");
        }
        newStpRoots[rootId] = true;
      }
    });
    // Remove previous STP roots
    Ext.Object.each(me.currentStpRoots, function(k){
      if(!newStpRoots[k]){
        // Remove node style
        me.objectNodes[k].attr("text/class", "");
      }
    });
    me.currentStpRoots = newStpRoots;
  },

  setStpBlocked: function(blocked){
    var me = this,
      newStpBlocked = {};
    Ext.each(me.graph.getLinks(), function(link){
      var linkId = link.get("data").id;
      if(blocked.indexOf(linkId) !== -1){
        newStpBlocked[linkId] = true;
        me.renderer.setLinkStyle(link, me.renderer.LINK_STP_BLOCKED);
      }
    });
    // @todo: Remove changed styles
    me.currentStpBlocked = newStpBlocked;
    console.log("blocked", me.currentStpBlocked);
  },

  onResize: function(){
    var me = this;
    if("paper" in me){
      me.renderer.setPaperDimension();
    }
  },

  changeLabelText: function(showIPAddress){
    this.renderer.changeLabelText(showIPAddress);
  },

  setPaperDimension: function(){
    this.renderer.setPaperDimension();
  },
});
