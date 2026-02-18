//---------------------------------------------------------------------
// Network Map Renderer
//---------------------------------------------------------------------
// Copyright (C) 2007-2026 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.MapRenderer");

Ext.define("NOC.inv.map.MapRenderer", {
  requires: ["NOC.inv.map.ShapeRegistry"],

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
    0: "gf-unknown",
    1: "gf-ok",
    2: "gf-warn",
    3: "gf-unknown",
    4: "gf-fail",
  },

  // Link status
  LINK_OK: 0,
  LINK_ADMIN_DOWN: 1,
  LINK_OPER_DOWN: 2,
  LINK_STP_BLOCKED: 3,

  constructor: function(panel){
    this.panel = panel;
    this.shapeRegistry = NOC.inv.map.ShapeRegistry;
    this.usedImages = {};
  },

  initFilters: function(){
    var me = this;
    // Apply SVG filters
    Ext.Object.each(me.svgFilters, function(fn){
      var ft = me.getFilter(fn, me.svgFilters[fn]),
        fd = V(ft);
      V(me.panel.paper.svg).defs().append(fd);
    });
    Ext.each(me.svgDefaultFilters, function(f){
      V(me.panel.paper.svg).defs().append(V(f));
    });
  },

  renderMap: function(data){
    var me = this,
      panel = me.panel,
      paper = panel.paper,
      graph = panel.graph,
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

    if(data?.normalize_position === false){ // Configured Map
      panel.isConfiguredMap = true;
      panel.bg_width = data.width;
      panel.bg_height = data.height;
    } else{
      panel.isConfiguredMap = false;
    }

    panel.isInteractive = false;
    panel.isDirty = false;
    panel.currentHighlight = null;
    panel.objectNodes = {};
    panel.linkBw = {};
    panel.objectsList = [];
    panel.portObjects = {};
    panel.interfaceMetrics = [];
    panel.currentStpRoots = {};
        
    graph.clear();
    paper.setGridSize(data.grid_size);
    panel.pollingInterval =
            data.object_status_refresh_interval * 1000 || panel.pollingInterval;
        
    // Set background
    if(data.background_image){
      backgroundOpt = {
        image: "/main/imagestore/" + data.background_image + "/image/",
        position: "left top;",
        opacity: data.background_opacity / 100,
      };
    }
    paper.drawBackground(backgroundOpt);
        
    // Create nodes
    Ext.each(data.nodes, function(node){
      if(
        !panel.app.viewAllNodeButton.pressed &&
                data.links.length > data.max_links &&
                node.external === true
      ){
        // skip create
        return;
      }
      pushNodeAndBadges(me.createNode(node));
      Ext.each(node.ports, function(port){
        panel.portObjects[port.id] = node.id;
        Ext.each(port.ports, function(ifname){
          panel.interfaceMetrics.push({
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
        panel.objectNodes[panel.portObjects[link.ports[0]]] &&
                panel.objectNodes[panel.portObjects[link.ports[1]]]
      )
        links.push(me.createLink(link));
    });

    graph.addCells(nodes);
    graph.addCells(links);
    graph.addCells(badges);
        
    panel.viewPort = me.createViewPort();
    graph.addCell(panel.viewPort);
    paper.findViewByModel(panel.viewPort).$el.hide();
        
    // Run status polling
    if(panel.statusPollingTaskId){
      panel.getObjectStatus();
    } else{
      panel.statusPollingTaskId = Ext.TaskManager.start({
        run: panel.getObjectStatus,
        interval: panel.pollingInterval,
        scope: panel,
      });
    }
        
    panel.hasStp = data.caps.indexOf("Network | STP") !== -1;
    panel.app.viewStpButton.setDisabled(!panel.hasStp);
    me.setPaperDimension();
    panel.fireEvent("renderdone");
  },

  createNode: function(data){
    var me = this,
      panel = me.panel,
      paper = panel.paper,
      badges = [],
      sclass,
      node;
        
    var dataName = data.name;
    if(dataName.indexOf("#") > 0){
      var tokens = data.name.split("#");
      tokens.pop();
      dataName = tokens.join("#");
    }
    var name = me.symbolName(dataName, data.metrics_label, data.shape_width || 64, true);
        
    if(Ext.isEmpty(data.glyph)){
      if(!me.usedImages[data.shape]){
        var img = me.shapeRegistry.getImage(data.shape);
        V(paper.svg).defs().append(V(img));
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
    } else{
      node = me.shapeRegistry.getIconNode(data, name);
    }
        
    Ext.each(data.shape_overlay, function(config){
      var badge = me.createBadge(node, config);
      node.embed(badge);
      badges.push(badge);
    });
        
    panel.objectNodes[data.id] = node;
    panel.objectsList.push({
      node_type: data.type,
      node_id: data.node_id,
      id: data.id,
      object_filter: data.object_filter,
      metrics_template: data.metrics_template,
    });
        
    return {
      node: node,
      badges: badges,
    };
  },

  createLink: function(data){
    var me = this,
      panel = me.panel,
      cfg,
      src,
      dst,
      getConnectionStyle = function(bw){
        for(var i = 0; i < me.bwStyle.length; i++){
          var s = me.bwStyle[i];
          if(s[0] <= bw){
            return s[1];
          }
        }
      };

    src = panel.objectNodes[panel.portObjects[data.ports[0]]];
    dst = panel.objectNodes[panel.portObjects[data.ports[1]]];

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
      cfg.connector = {
        name: data.connector,
      };
    } else{
      cfg.connector = {
        name: "normal",
      };
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
    panel.linkBw[data.id] = {
      in: data.in_bw,
      out: data.out_bw,
    };
    //
    return new joint.dia.Link(cfg);
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
      size: {
        width: size,
        height: size,
      },
      attrs: {
        body: {
          strokeWidth: 0.5,
        },
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

  createViewPort: function(){
    return new joint.shapes.standard.Rectangle({
      position: {
        x: 0,
        y: 0,
      },
      size: {
        width: 100,
        height: 100,
      },
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


  // Link overlay modes
  LO_NONE: 0,
  LO_LOAD: 1,

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
    luStyle = Ext.apply({
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
    link.label(0, {
      attrs: {
        text: luStyle,
      },
    });
    link.label(0, {
      position: 0.5,
    });
  },

  setLoadOverlayData: function(data){
    var me = this,
      panel = me.panel;
    Ext.each(panel.graph.getLinks(), function(link){
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
      } else if(!panel.currentStpBlocked[linkId]){
        // Get bandwidth
        sIn = getTotal(ports[0], "Interface | Load | In");
        sOut = getTotal(ports[0], "Interface | Load | Out");
        dIn = getTotal(ports[1], "Interface | Load | In");
        dOut = getTotal(ports[1], "Interface | Load | Out");

        bw = panel.linkBw[linkId];
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
                ".": {
                  filter: {
                    name: "dropShadow",
                    args: {
                      dx: 1,
                      dy: 1,
                      blur: 2,
                    },
                  },
                },
              });
              break;
            }
          }
        }
        // Show balance point
        tb = td + dt;
        if(tb > 0){
          balance = td / tb;
          link.label(0, {
            position: balance,
          });
          if(luStyle){
            luStyle.fill = luStyle.stroke;
            luStyle.visibility = "visible";
            luStyle.text = "\uf111";
            luStyle["font-size"] = 5;
            link.label(0, {
              attrs: {
                text: luStyle,
              },
            });
          }
        }
        // save link utilization
        var values = [];
        Ext.each(ports, function(port){
          var metrics = [],
            metricsName = ["Interface | Load | In", "Interface | Load | Out"];
          Ext.each(metricsName, function(metric){
            var value = "-";
            if(data?.[port]?.[metric] !== undefined){
              value = getTotal(port, metric);
            }
            metrics.push({
              metric: metric,
              value: value,
            });
          });
          values.push({
            port: port,
            metrics: metrics,
          });
        });
        link.set("data", Ext.apply({
          metrics: values,
        }, link.get("data")));
      }
    });
  },

  resetOverlayData: function(){
    var me = this,
      panel = me.panel;
    Ext.each(panel.graph.getLinks(), function(link){
      link.attr({
        ".connection": {
          stroke: "black",
        },
        ".": {
          filter: "none",
        },
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

  applyObjectStatuses: function(data){
    var me = this,
      panel = me.panel;
    Ext.Object.each(data, function(s){
      var node = panel.objectNodes[s];
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
          var wrench = me.createBadge(node, {
            position: "NE",
            form: "c",
            code: 61613,
          });
          node.attributes.data.isMaintenance = true;
          wrench.set("data", {
            type: "wrench",
          });
          node.embed(wrench);
          panel.graph.addCell(wrench);
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

  changeLabelText: function(showIPAddress){
    var me = this,
      panel = me.panel;
    Ext.each(panel.graph.getElements(), function(e){
      e.attr(
        "text/text",
        me.symbolName(
          showIPAddress ? e.get("address") : e.get("name"),
          e.get("data").metrics_label,
          e.get("data").shape_width,
          false,
        ),
      );
    }, this);
  },

  setPaperDimension: function(zoom){
    var me = this,
      panel = me.panel,
      paddingX = 15,
      paddingY = 15,
      w = panel.getWidth(),
      h = panel.getHeight();

    if(panel.paper){
      panel.paper.fitToContent();
      var contentBB = panel.paper.getContentBBox();
      if(contentBB && contentBB.width && contentBB.height){
        if(panel.isConfiguredMap){
          w = panel.bg_width * (zoom || 1);
          h = panel.bg_height * (zoom || 1);
        } else{
          w = Ext.Array.max([contentBB.width, panel.getWidth()]);
          h = Ext.Array.max([contentBB.height, panel.getHeight()]);
          panel.paper.translate(-1 * contentBB.x + paddingX, -1 * contentBB.y + paddingY);
        }
        panel.paper.setDimensions(w + paddingX * 2, h + paddingY * 2);
      }
      panel.setViewPortSize();
    }
  },

  setZoom: function(zoom){
    var me = this;
    me.panel.paper.scale(zoom, zoom);
    me.setPaperDimension(zoom);
  },

  symbolName: function(name, metrics_label, shape_width, makeBrake){
    var metrics, breakText = name;
    if(makeBrake){
      breakText = this.breakText(name, {
        width: shape_width * 2,
      });
    }
    if(!Ext.isEmpty(metrics_label)){
      metrics = metrics_label.split("<br/>");
      metrics = Ext.Array.map(metrics, function(metric){
        return this.breakText(metric, {
          width: shape_width * 2,
        });
      }, this);
      return breakText + "\n" + metrics.join("\n");
    } else{
      return breakText;
    }
  },

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
            heightValue = {
              value: 1.5,
              unit: "em",
            };
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
});