//---------------------------------------------------------------------
// Network Map Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.MapPanel");

Ext.define("NOC.inv.map.MapPanel", {
  extend: "Ext.panel.Panel",
  requires: ["NOC.inv.map.ShapeRegistry"],
  layout: "fit",
  scrollable: true,
  app: null,
  readOnly: false,
  pollingInterval: 180000,
  updatedPollingTaskId: null,
  svgFilters: {
    // Asbestos, #7f8c8d
    osUnknown: [127, 140, 141],
    // Emerald, #23cc71
    osOk: [46, 204, 113],
    // Sunflower, #f1c40f
    osAlarm: [241, 196, 15],
    // #404040
    osUnreach: [64, 64, 64],
    // Pomegranade, #c0392b
    osDown: [192, 57, 43],
  },

  CAP_STP: "Network | STP",

  svgDefaultFilters: [
    '<filter id="highlight">' +
      '<feGaussianBlur stdDeviation="4" result="coloredBlur"/>' +
      "<feMerge>" +
      '<feMergeNode in="coloredBlur"/>' +
      '<feMergeNode in="SourceGraphic"/>' +
      "</feMerge>" +
      "</filter>",

    '<filter id="glow" filterUnits="userSpaceOnUse">' +
      '<feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>' +
      "<feMerge>" +
      '<feMergeNode in="coloredBlur"/>' +
      '<feMergeNode in="SourceGraphic"/>' +
      "</feMerge>" +
      "</filter>",

    '<filter x="0" y="0" width="1" height="1" id="solid">' +
      '<feFlood flood-color="rgb(236,240,241)"/>' +
      '<feComposite in="SourceGraphic"/>' +
      "</filter>",
  ],

  // Link bandwidth style
  bwStyle: [
    [99500000000, {"stroke-width": "5px"}], // 100G >= STM-640
    [39500000000, {"stroke-width": "4px"}], // 40G >= STM-256
    [9500000000, {"stroke-width": "3px"}], // 10G >= STM-64
    [1000000000, {"stroke-width": "2px"}], // 1G
    [100000000, {"stroke-width": "1px"}], // 100M
    [0, {"stroke-width": "1px", "stroke-dasharray": "10 5"}],
  ],
  // Link utilization style
  luStyle: [
    [0.95, {stroke: "#ff0000"}],
    [0.8, {stroke: "#990000"}],
    [0.5, {stroke: "#ff9933"}],
    [0.0, {stroke: "#006600"}],
  ],
  adminDownStyle: {
    stroke: "#7f8c8d",
  },
  operDownStyle: {
    stroke: "#c0392b",
  },
  stpBlockedStyle: {
    stroke: "#8e44ad",
  },
  // Object status filter names
  statusFilter: {
    0: "osUnknown",
    1: "osOk",
    2: "osAlarm",
    3: "osUnreach",
    4: "osDown",
  },

  // Link overlay modes
  LO_NONE: 0,
  LO_LOAD: 1,
  // Link status
  LINK_OK: 0,
  LINK_ADMIN_DOWN: 1,
  LINK_OPER_DOWN: 2,
  LINK_STP_BLOCKED: 3,

  resizeHandles: "onResize",

  initComponent: function(){
    var me = this;

    me.shapeRegistry = NOC.inv.map.ShapeRegistry;
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
    new_load_scripts(
      [
        "/ui/pkg/lodash/lodash.min.js",
        "/ui/pkg/backbone/backbone.min.js",
        "/ui/pkg/joint/joint.min.js",
      ],
      me,
      me.initMap,
    );
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
  createViewPort: function(){
    return new joint.shapes.standard.Rectangle({
      position: {x: 0, y: 0},
      size: {width: 100, height: 100},
      attrs: {
        rect: {
          stroke: "gray",
          "stroke-width": 1,
          vectorEffect: "non-scaling-stroke",
        },
      },
      z: -1,
    });
  },
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
    Ext.Object.each(me.svgFilters, function(fn){
      var ft = me.getFilter(fn, me.svgFilters[fn]),
        fd = V(ft);
      V(me.paper.svg).defs().append(fd);
    });
    Ext.each(me.svgDefaultFilters, function(f){
      V(me.paper.svg).defs().append(V(f));
    });
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
    var me = this,
      backgroundOpt = {},
      nodes = [],
      badges = [],
      links = [],
      pushNodeAndBadges = function(data){
        nodes.push(data.node);
        if(data.badges.length){
          badges.push(data.badges);
        }
      };
    if(
      data.hasOwnProperty("normalize_position") &&
      data.normalize_position === false
    ){
      me.normalize_position = data.normalize_position;
      me.bg_width = data.width;
      me.bg_height = data.height;
    }
    me.isInteractive = false;
    me.isDirty = false;
    me.currentHighlight = null;
    me.objectNodes = {};
    me.linkBw = {};
    me.objectsList = [];
    me.interfaceMetrics = [];
    me.currentStpRoots = {};
    me.graph.clear();
    me.paper.setGridSize(data.grid_size);
    me.pollingInterval =
      data.object_status_refresh_interval * 1000 || me.pollingInterval;
    // Set background
    if(data.background_image){
      backgroundOpt = {
        image: "/main/imagestore/" + data.background_image + "/image/",
        position: "left top;",
        opacity: data.background_opacity / 100,
      };
    }
    me.paper.drawBackground(backgroundOpt);
    // Create nodes
    Ext.each(data.nodes, function(node){
      if(
        !me.app.viewAllNodeButton.pressed &&
        data.links.length > data.max_links &&
        node.external === true
      ){
        // skip create
        return;
      }
      pushNodeAndBadges(me.createNode(node));
      Ext.each(node.ports, function(port){
        me.portObjects[port.id] = node.id;
        Ext.each(port.ports, function(ifname){
          me.interfaceMetrics.push({
            id: port.id,
            tags: {
              object: node.name,
              interface: ifname,
            },
          });
        });
      });
    });
    // Create links
    Ext.each(data.links, function(link){
      if(
        me.objectNodes[me.portObjects[link.ports[0]]] &&
        me.objectNodes[me.portObjects[link.ports[1]]]
      )
        links.push(me.createLink(link));
    });
    me.graph.addCells(nodes);
    me.graph.addCells(links);
    me.graph.addCells(badges);
    me.viewPort = me.createViewPort();
    me.graph.addCell(me.viewPort);
    me.paper.findViewByModel(me.viewPort).$el.hide();
    // Run status polling
    if(me.statusPollingTaskId){
      me.getObjectStatus();
    } else{
      me.statusPollingTaskId = Ext.TaskManager.start({
        run: me.getObjectStatus,
        interval: me.pollingInterval,
        scope: me,
      });
    }
    me.hasStp = data.caps.indexOf("Network | STP") !== -1;
    me.app.viewStpButton.setDisabled(!me.hasStp);
    me.setPaperDimension();
    me.fireEvent("renderdone");
  },
  //
  createNode: function(data){
    var me = this,
      badges = [],
      sclass,
      node;
    var dataName = data.name;
    if(dataName.indexOf("#") > 0){
      var tokens = data.name.split("#");
      tokens.pop();
      dataName = tokens.join("#");
    }
    var name = this.symbolName(dataName, data.metrics_label, data.shape_width, true);
    if(!me.usedImages[data.shape]){
      var img = me.shapeRegistry.getImage(data.shape);
      V(me.paper.svg).defs().append(V(img));
      me.usedImages[data.shape] = true;
    }
    sclass = me.shapeRegistry.getShape(data.shape);
    node = new sclass({
      id: data.type + ":" + data.id,
      z: 9999,
      external: data.external,
      name: name,
      address: data.address,
      position: {
        x: data.x,
        y: data.y,
      },
      attrs: {
        text: {
          text: name,
        },
        use: {
          width: data.shape_width,
          height: data.shape_height,
        },
      },
      size: {
        width: data.shape_width,
        height: data.shape_height,
      },
      data: {
        type: data.type,
        id: data.id,
        node_id: data.node_id,
        caps: data.caps,
        isMaintenance: false,
        portal: data.portal,
        object_filter: data.object_filter,
        metrics_template: data.metrics_template,
        shape_width: data.shape_width,
        metrics_label: data.metrics_label,
      },
    });
    Ext.each(data.shape_overlay, function(config){
      var badge = me.createBadge(node, config);
      node.embed(badge);
      badges.push(badge);
    });
    me.objectNodes[data.id] = node;
    me.objectsList.push({
      node_type: data.type,
      node_id: data.node_id,
      id: data.id,
      object_filter: data.object_filter,
      metrics_template: data.metrics_template,
    });
    return {node: node, badges: badges};
  },
  //
  createLink: function(data){
    var me = this,
      cfg,
      src,
      dst,
      connector,
      getConnectionStyle = function(bw){
        for(var i = 0; i < me.bwStyle.length; i++){
          var s = me.bwStyle[i];
          if(s[0] <= bw){
            return s[1];
          }
        }
      };

    src = me.objectNodes[me.portObjects[data.ports[0]]];
    dst = me.objectNodes[me.portObjects[data.ports[1]]];

    cfg = {
      id: data.type + ":" + data.id,
      z: 8888,
      source: {
        id: src,
      },
      target: {
        id: dst,
      },
      attrs: {
        ".tool-remove": {
          display: "none", // Disable "Remove" circle
        },
        ".marker-arrowheads": {
          display: "none", // Do not show hover arrowheads
        },
        ".connection": getConnectionStyle(data.bw),
      },
      data: {
        type: data.type,
        id: data.id,
        ports: data.ports,
      },
      labels: [
        // Balance marker
        // @todo: Make hidden by default
        {
          position: 0.5,
          attrs: {
            text: {
              fill: "black",
              text: __("\uf111"),
              "font-family": "FontAwesome",
              "font-size": 5,
              visibility: "hidden",
            },
            rect: {
              visibility: "hidden",
            },
          },
        },
      ],
    };
    //
    if(data.connector){
      cfg.connector = {name: data.connector};
    } else{
      cfg.connector = {name: "normal"};
    }

    if(data.vertices && data.vertices.length > 0){
      cfg.vertices = data.vertices;
    }
    //
    if(src.get("external")){
      cfg["attrs"][".marker-source"] = {
        fill: "black",
        d: "M 10 0 L 0 5 L 10 10 z",
      };
    }
    if(dst.get("external")){
      cfg["attrs"][".marker-target"] = {
        fill: "black",
        d: "M 10 0 L 0 5 L 10 10 z",
      };
    }
    //
    me.linkBw[data.id] = {
      in: data.in_bw,
      out: data.out_bw,
    };
    //
    return new joint.dia.Link(cfg);
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
    me.setPaperDimension();
  },
  //
  save: function(){
    var me = this,
      r = {
        nodes: [],
        links: [],
      };
    if(me.normalize_position){
      var bbox = me.paper.getContentBBox();
      r.width = bbox.width - bbox.x;
      r.height = bbox.height - bbox.y;
    }
    // Get nodes position
    Ext.each(me.graph.getElements(), function(e){
      if("wrench" !== e.get("data").type && "badge" !== e.get("data").type){
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
      success: function(response){
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
        me.applyObjectStatuses(data);
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

  resetOverlayData: function(){
    var me = this;
    Ext.each(me.graph.getLinks(), function(link){
      link.attr({
        ".connection": {
          stroke: "black",
        },
        ".": {filter: "none"},
      });

      link.label(0, {
        attrs: {
          text: {
            visibility: "hidden",
          },
        },
      });
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
            me.setLoadOverlayData(Ext.decode(response.responseText));
          },
          failure: Ext.emptyFn,
        });
        break;
    }
  },

  createBadge: function(node, config){
    var nodeSize = node.get("size"),
      size = Math.max(Math.min(nodeSize.height / 3, nodeSize.width / 3), 18),
      shape = config.form === "s" ? "Rectangle" : "Circle",
      // default NE
      x = node.get("position").x + nodeSize.width - 0.62 * size,
      y = node.get("position").y - 0.38 * size;
    switch(config.position){
      case "N":
        x = node.get("position").x + nodeSize.width / 2 - size / 2;
        y = node.get("position").y - 0.38 * size;
        break;
      case "E":
        x = node.get("position").x + nodeSize.width - 0.62 * size;
        y = node.get("position").y + size;
        break;
      case "SE":
        x = node.get("position").x + nodeSize.width - 0.62 * size;
        y = node.get("position").y + 2.25 * size;
        break;
      case "S":
        x = node.get("position").x + nodeSize.width / 2 - size / 2;
        y = node.get("position").y + 2.25 * size;
        break;
      case "SW":
        x = node.get("position").x - 0.38 * size;
        y = node.get("position").y + 2.25 * size;
        break;
      case "W":
        x = node.get("position").x - 0.38 * size;
        y = node.get("position").y + size;
        break;
      case "NW":
        x = node.get("position").x - 0.38 * size;
        y = node.get("position").y - 0.38 * size;
        break;
    }
    return new joint.shapes.standard[shape]({
      position: {
        x: x,
        y: y,
      },
      size: {width: size, height: size},
      attrs: {
        body: {strokeWidth: 0.5},
        text: {
          text: String.fromCharCode(config.code),
          "font-family": "FontAwesome",
          "font-size": size / 1.7,
        },
      },
      data: {
        type: "badge",
      },
    });
  },

  applyObjectStatuses: function(data){
    var me = this;
    Ext.Object.each(data, function(s){
      var node = me.objectNodes[s];
      if(!node){
        return;
      }
      // Update metrics
      node.attr(
        "text/text",
        me.symbolName(
          node.attributes.name,
          data[s].metrics_label,
          node.attributes.data.shape_width,
          false,
        ),
      );
      node.attributes.data.metrics_label = data.metrics_label;
      node.attributes.text = node.setFilter(
        me.statusFilter[data[s].status_code & 0x1f],
      ); // Remove maintenance bit
      if(data[s].status_code & 0x20){
        // Maintenance mode
        if(!node.get("data").isMaintenance){
          var wrench = me.createBadge(node, {position: "NE", form: "c", code: 61613});
          node.attributes.data.isMaintenance = true;
          wrench.set("data", {type: "wrench"});
          node.embed(wrench);
          me.graph.addCell(wrench);
        }
      } else{
        if(node.get("data").isMaintenance){
          var embeddedCells = node.getEmbeddedCells();
          node.attributes.data.isMaintenance = false;
          Ext.each(embeddedCells, function(cell){
            if(cell.get(data) && cell.get(data).type === "wrench"){
              node.unembed(cell);
              cell.remove();
            }
          });
        }
      }
    });
  },
  //
  svgFilterTpl: new Ext.XTemplate(
    '<filter id="{id}">',
    '<feColorMatrix type="matrix" color-interpolation-filters="sRGB" ',
    'values="',
    "{r0} 0    0    0 {r1} ",
    "0    {g0} 0    0 {g1} ",
    "0    0    {b0} 0 {b1} ",
    '0    0    0    1 0    " />',
    "</filter>",
  ),
  //
  // Get SVG filter text
  //   c = [R, G, B]
  //
  getFilter: function(filterId, c){
    var me = this,
      r1 = c[0] / 256.0,
      g1 = c[1] / 256.0,
      b1 = c[2] / 256.0,
      r0 = (256.0 - c[0]) / 256.0,
      g0 = (256.0 - c[1]) / 256.0,
      b0 = (256.0 - c[2]) / 256.0;
    return me.svgFilterTpl.apply({
      id: filterId,
      r0: r0,
      r1: r1,
      g0: g0,
      g1: g1,
      b0: b0,
      b1: b1,
    });
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
      me.resetOverlayData();
    } else{
      me.getOverlayData();
    }
  },

  // Display links load
  // data is dict of
  // metric -> {ts: .., value: }
  setLoadOverlayData: function(data){
    var me = this;
    Ext.each(me.graph.getLinks(), function(link){
      var sIn,
        sOut,
        dIn,
        dOut,
        bw,
        td,
        dt,
        lu,
        cfg,
        tb,
        balance,
        ports = link.get("data").ports,
        linkId = link.get("data").id,
        luStyle = null,
        getTotal = function(port, metric){
          if(data[port] && data[port][metric]){
            return data[port][metric];
          } else{
            return 0.0;
          }
        },
        hasMetric = function(port, metric){
          return data.hasOwnProperty(port) && data[port].hasOwnProperty(metric);
        },
        getStatus = function(port, status){
          if(data[port] && data[port][status] !== undefined){
            return data[port][status];
          } else{
            return true;
          }
        };
      //
      if(
        !getStatus(ports[0], "admin_status") ||
        !getStatus(ports[1], "admin_status")
      ){
        me.setLinkStyle(link, me.LINK_ADMIN_DOWN);
      } else if(
        !getStatus(ports[0], "oper_status") ||
        !getStatus(ports[1], "oper_status")
      ){
        me.setLinkStyle(link, me.LINK_OPER_DOWN);
      } else if(!me.currentStpBlocked[linkId]){
        // Get bandwidth
        sIn = getTotal(ports[0], "Interface | Load | In");
        sOut = getTotal(ports[0], "Interface | Load | Out");
        dIn = getTotal(ports[1], "Interface | Load | In");
        dOut = getTotal(ports[1], "Interface | Load | Out");

        bw = me.linkBw[linkId];
        // Destination to target
        td = Math.max(sOut, dIn);
        // Target to destination
        dt = Math.max(sIn, dOut);
        if(bw){
          // Link utilization
          lu = 0.0;
          if(bw.in){
            lu = Math.max(lu, dt / bw.in);
          }
          if(bw.out){
            lu = Math.max(lu, td / bw.out);
          }
          // Apply proper style according to load
          for(var i = 0; i < me.luStyle.length; i++){
            var t = me.luStyle[i][0],
              style = me.luStyle[i][1];
            if(lu >= t){
              cfg = {};
              cfg = Ext.apply(cfg, style);
              luStyle = cfg;
              link.attr({
                ".connection": cfg,
                ".": {filter: {name: "dropShadow", args: {dx: 1, dy: 1, blur: 2} } },
              });
              break;
            }
          }
        }
        // Show balance point
        tb = td + dt;
        if(tb > 0){
          balance = td / tb;
          link.label(0, {position: balance});
          if(luStyle){
            luStyle.fill = luStyle.stroke;
            luStyle.visibility = "visible";
            luStyle.text = "\uf111";
            luStyle["font-size"] = 5;
            link.label(0, {attrs: {text: luStyle} });
          }
        }
        // save link utilization
        var values = [];
        Ext.each(ports, function(port){
          var metrics = [],
            metricsName = ["Interface | Load | In", "Interface | Load | Out"];
          Ext.each(metricsName, function(metric){
            var value = "-";
            if(hasMetric(port, metric)){
              value = getTotal(port, metric);
            }
            metrics.push({metric: metric, value: value});
          });
          values.push({port: port, metrics: metrics});
        });
        link.set("data", Ext.apply({metrics: values}, link.get("data")));
      }
    });
  },

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
    me.paper.scale(zoom, zoom);
    me.setPaperDimension(zoom);
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
      if(
        v.attributes.data.hasOwnProperty("caps") &&
        v.attributes.data.caps.indexOf(me.CAP_STP) !== -1
      ){
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
        me.setLinkStyle(link, me.LINK_STP_BLOCKED);
      }
    });
    // @todo: Remove changed styles
    me.currentStpBlocked = newStpBlocked;
    console.log("blocked", me.currentStpBlocked);
  },

  setLinkStyle: function(link, status){
    var me = this,
      style,
      glyph,
      fontSize = 10,
      luStyle;

    switch(status){
      case me.LINK_OK:
        break;
      case me.LINK_ADMIN_DOWN:
        style = me.adminDownStyle;
        glyph = "\uf00d";
        break;
      case me.LINK_OPER_DOWN:
        style = me.operDownStyle;
        glyph = "\uf071";
        break;
      case me.LINK_STP_BLOCKED:
        style = me.stpBlockedStyle;
        glyph = "\uf05e";
        fontSize = 12;
        break;
    }
    //
    link.attr({
      ".connection": style,
    });
    luStyle = Ext.apply(
      {
        attrs: {
          text: style,
        },
        visibility: "visible",
        position: 0.5,
        fill: style.stroke,
      },
      style,
    );
    // @todo: Remove?
    luStyle.fill = luStyle.stroke;
    luStyle.visibility = "visible";
    luStyle.text = glyph;
    luStyle["font-size"] = fontSize;
    link.label(0, {attrs: {text: luStyle} });
    link.label(0, {position: 0.5});
  },

  onResize: function(width, height){
    var me = this;
    if("paper" in me){
      me.setPaperDimension();
    }
  },

  setPaperDimension: function(zoom){
    var me = this,
      paddingX = 15,
      paddingY = 15,
      w = me.getWidth(),
      h = me.getHeight();

    if(me.paper){
      me.paper.fitToContent();
      var contentBB = me.paper.getContentBBox();
      if(contentBB && contentBB.width && contentBB.height){
        if(me.normalize_position){
          w = Ext.Array.max([contentBB.width, me.getWidth()]);
          h = Ext.Array.max([contentBB.height, me.getHeight()]);
          me.paper.translate(-1 * contentBB.x + paddingX, -1 * contentBB.y + paddingY);
        } else{
          w = me.bg_width * (zoom || 1);
          h = me.bg_height * (zoom || 1);
        }
        me.paper.setDimensions(w + paddingX * 2, h + paddingY * 2);
      }
      me.setViewPortSize();
    }
  },

  changeLabelText: function(showIPAddress){
    Ext.each(this.graph.getElements(), function(e){
      e.attr(
        "text/text",
        this.symbolName(
          showIPAddress ? e.get("address") : e.get("name"),
          e.get("data").metrics_label,
          e.get("data").shape_width,
          false,
        ),
      );
    }, this);
  },
  //
  breakText: function(text, size, styles, opt){
    opt = opt || {};
    var width = size.width;
    var height = size.height;
    var svgDocument = opt.svgDocument || V("svg").node;
    var textElement = V("<text><tspan></tspan></text>").attr(styles || {}).node;
    var textSpan = textElement.firstChild;
    var textNode = document.createTextNode("");

    // Prevent flickering
    textElement.style.opacity = 0;
    // Prevent FF from throwing an uncaught exception when `getBBox()`
    // called on element that is not in the render tree (is not measurable).
    // <tspan>.getComputedTextLength() returns always 0 in this case.
    // Note that the `textElement` resp. `textSpan` can become hidden
    // when it's appended to the DOM and a `display: none` CSS stylesheet
    // rule gets applied.
    textElement.style.display = "block";
    textSpan.style.display = "block";
    textSpan.appendChild(textNode);
    svgDocument.appendChild(textElement);
    if(!opt.svgDocument){
      document.body.appendChild(svgDocument);
    }

    var words = text.split(/(\W+)/);
    var full = [];
    var lines = [];
    var p;
    var lineHeight;

    for(var i = 0, l = 0, len = words.length; i < len; i++){
      var word = words[i];

      textNode.data = lines[l] ? lines[l] + word : word;
      if(textSpan.getComputedTextLength() <= width){
        // the current line fits
        lines[l] = textNode.data;
        if(p){
          // We were partitioning. Put rest of the word onto next line
          full[l++] = true;
          // cancel partitioning
          p = 0;
        }
      } else{
        if(!lines[l] || p){
          var partition = !!p;
          p = word.length - 1;
          if(partition || !p){
            // word has only one character.
            if(!p){
              if(!lines[l]){
                // we won't fit this text within our rect
                lines = [];
                break;
              }
              // partitioning didn't help on the non-empty line
              // try again, but this time start with a new line
              // cancel partitions created
              words.splice(i, 2, word + words[i + 1]);
              // adjust word length
              len--;
              full[l++] = true;
              i--;
              continue;
            }
            // move last letter to the beginning of the next word
            words[i] = word.substring(0, p);
            words[i + 1] = word.substring(p) + words[i + 1];
          } else{
            // We initiate partitioning
            // split the long word into two words
            words.splice(i, 1, word.substring(0, p), word.substring(p));
            // adjust words length
            len++;
            if(l && !full[l - 1]){
              // if the previous line is not full, try to fit max part of
              // the current word there
              l--;
            }
          }
          i--;
          continue;
        }
        l++;
        i--;
      }
      // if size.height is defined we have to check whether the height of the entire
      // text exceeds the rect height
      if(height !== undefined){
        if(lineHeight === undefined){
          var heightValue;
          // use the same defaults as in V.prototype.text
          if(styles.lineHeight === "auto"){
            heightValue = {value: 1.5, unit: "em"};
          } else{
            heightValue = joint.util.parseCssNumeric(styles.lineHeight, ["em"]) || {
              value: 1,
              unit: "em",
            };
          }
          lineHeight = heightValue.value;
          if(heightValue.unit === "em"){
            lineHeight *= textElement.getBBox().height;
          }
        }
        if(lineHeight * lines.length > height){
          // remove overflowing lines
          lines.splice(Math.floor(height / lineHeight));
          break;
        }
      }
    }
    if(opt.svgDocument){
      // svg document was provided, remove the text element only
      svgDocument.removeChild(textElement);
    } else{
      // clean svg document
      document.body.removeChild(svgDocument);
    }
    return lines.join("\n");
  },
  //
  symbolName: function(name, metrics_label, shape_width, makeBrake){
    var metrics, breakText = name;
    if(makeBrake){
      breakText = this.breakText(name, {width: shape_width * 2});
    }
    if(!Ext.isEmpty(metrics_label)){
      metrics = metrics_label.split("<br/>");
      metrics = Ext.Array.map(metrics, function(metric){
        return this.breakText(metric, {width: shape_width * 2});
      }, this);
      return breakText + "\n" + metrics.join("\n");
    } else{
      return breakText;
    }
  },
});
