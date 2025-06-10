//----------------------------------------------------------------------
// Various javascript utilities
//----------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------

// NOC namespace
Ext.namespace("NOC", "NOC.render", "NOC.msg");

//
// Custom column renderers
//
Ext.apply(NOC.render, {
  //
  // NOC.render.Bool(v)
  //     Grid field renderer for boolean values
  //     Displays icons depending on true/false status
  //
  Bool: function(v){
    return {
      true: "<i class='fa fa-check' style='color:" + NOC.colors.yes + "'></i>",
      false: "<i class='fa fa-times' style='color:" + NOC.colors.no + "'></i>",
      null: "<i class='fa fa-circle-o'></i>",
    }[v];
  },
  //
  // NOC.render.Yes(v)
  //    Grid field renderer for boolean values
  //    Displays icon only for true
  Yes: function(v){
    return {
      true: "<i class='fa fa-check' style='color:" + NOC.colors.yes + "'></i>",
      false: "",
      null: "",
    }[v];
  },
  //
  // NOC.render.No(v)
  //    Grid field renderer for boolean values
  //    Displays icon only for false
  No: function(v){
    return {
      true: "",
      false: "<i class='fa fa-times' style='color:" + NOC.colors.no + "'></i>",
      null: "",
    }[v];
  },

  //
  // NOC.render.URL(v)
  //      Grid field renderer for URLs
  //
  URL: function(v){
    return "<a href =' " + v + "' target='_'>" + v + "</a>";
  },

  //
  // NOC.render.Tags(v)
  //      Grid field renderer for tags
  //
  Tags: function(v){
    if(v){
      return v.map(function(x){
        return "<span class='x-display-tag'>" + x + "</span>";
      }).join(" ");
    } else{
      return "";
    }
  },

  //
  // NOC.render.LabelField(v)
  //      Grid field renderer for labels
  //
  LabelField: function(v){
    if(v){
      return v.map(function(x){
        return "<span class='x-display-tag'>" + (x.name ? x.name : x) + "</span>";
      }).join(" ");
    } else{
      return "";
    }
  },

  Lookup: function(name){
    var l = name + "__label";
    return function(value, meta, record){
      if(!Ext.isEmpty(value)){
        return record.get(l)
      } else{
        return "";
      }
    };
  },

  ObjectLookup: function(name){
    var l = name + "__label";
    return function(value, meta, record){
      if(!Ext.isEmpty(value)){
        return record[l];
      } else{
        return "";
      }
    };
  },

  Tooltip: function(fmt){
    var tpl = new Ext.XTemplate(fmt);
    return function(value, meta, record){
      var tooltip = tpl.apply(record.getData());
      return Ext.String.format(
        '<span title="{0}">{1}</span>',
        Ext.htmlEncode(tooltip),
        Ext.htmlEncode(value),
      );
    }
  },

  LookupTooltip: function(name, fmt){
    var lookup = NOC.render.Lookup(name),
      tooltip = NOC.render.Tooltip(fmt);
    return function(value, meta, record){
      return tooltip(
        lookup(value, meta, record),
        meta, record,
      )
    }
  },

  Clickable: function(value){
    return "<a href='#' class='noc-clickable-cell'>" + value + "</a>";
  },

  ClickableLookup: function(name){
    var l = name + "__label";
    return function(value, meta, record){
      var v = value ? record.get(l) : "...";
      return "<a href='#' class='noc-clickable-cell' title='Click to change...'>" + v + "</a>";
    };
  },

  WrapColumn: function(val){
    return "<div style='white-space:normal !important;'>" + val + "</div>";
  },

  Date: function(val){
    if(!val){
      return "";
    }
    return Ext.Date.format(val, "Y-m-d")
  },

  DateTime: function(val){
    if(!val){
      return "";
    }
    return Ext.Date.format(val, "Y-m-d H:i:s")
  },

  Choices: function(choices){
    return function(value){
      return choices[value];
    }
  },

  Label: function(v){
    let toHexColor = function(x){
      let hex = Number(x).toString(16);
      while(hex.length < 6){
        hex = "0" + hex;
      }
      return "#" + hex;
    };

    let name = v.name,
      scopedName = "",
      bg_color1 = toHexColor(v.bg_color1 || 0),
      fg_color1 = toHexColor(v.fg_color1 || 0),
      bg_color2 = toHexColor(v.bg_color2 || 0),
      fg_color2 = toHexColor(v.fg_color2 || 0),
      parts = name.split("::");
    if(parts.length > 1){
      scopedName = parts.pop();
      name = parts.join("::");
    }
    let r = [
      "<div class='x-noc-label' style='background-color:",
      bg_color1,
      ";border-color:",
      bg_color1,
      "'>",
    ];
    Ext.each(v.badges, function(badge){
      r.push("<i class='fa " + badge + "' style='color: " + fg_color1 + "' aria-hidden='true'></i>");
    });
    r.push("<div class='x-noc-label-text' style='color:" + fg_color1 +
            "'>");
    r.push(Ext.util.Format.htmlEncode(name));
    r.push("</div>");
    if(scopedName !== ""){
      r.push("<div class='x-noc-label-text-scoped' style='color:" +
                fg_color2 +
                ";background-color:" +
                bg_color2 +
                "'>");
      r.push(Ext.util.Format.htmlEncode(scopedName));
      r.push("</div>");
    }
    r.push("</div>");
    return r.join("");
  },

  Labels: function(v){
    v = v || [];
    return v.map(NOC.render.Label).join("");
  },

  Timestamp: function(val){
    if(!val){
      return "";
    }
    var d = new Date(val * 1000),
      y = d.getFullYear(),
      m = d.getMonth() + 1,
      D = d.getDate(),
      h = d.getHours(),
      M = d.getMinutes(),
      s = d.getSeconds(),
      f = function(v){
        return v <= 9 ? "0" + v : v;
      };
    return "" + y + "-" + f(m) + "-" + f(D) + " " +
            f(h) + ":" + f(M) + ":" + f(s);
  },

  Duration: function(val){
    var f = function(v){
      return v <= 9 ? "0" + v : v;
    };

    if(!val){
      return "";
    }
    val = +val;
    if(isNaN(val)){
      return "";
    }
    if(val < 1){
      // Msec
      return "" + val * 1000 + "ms";
    }
    if(val < 60){
      // XXs
      return "" + val + "s";
    }
    if(val < 86400){
      // HH:MM:SS
      var h = Math.floor(val / 3600),
        m = Math.floor((val - h * 3600) / 60),
        s = val - h * 3600 - m * 60;

      return f(h) + ":" + f(m) + ":" + f(s);
    }
    // DDd HHh
    var d = Math.floor(val / 86400),
      hh = Math.floor((val - d * 86400) / 3600);
    return "" + d + "d " + f(hh) + "h";
  },

  Size: function(v){
    if(v === null || v === undefined){
      return "";
    }
    if(v >= 10000000){
      return Math.round(v / 1000000) + "M";
    }
    if(v > 1000){
      return Math.round(v / 1000) + "K";
    }
    return "" + v;
  },

  Join: function(sep){
    return function(value){
      return value.join(sep);
    }
  },

  htmlEncode: function(v){
    if(v) return Ext.util.Format.htmlEncode(v);
    return "NULL";
  },

  //
  // NOC.render.Table accepts table configuration
  // and values as list of objects
  //
  // renderer: NOC.render.Table({
  //     columns: [
  //         {
  //             text: "Column Header 1",
  //             dataIndex: "field1"
  //         },
  //         {
  //             text: "Column Header 2",
  //             dataIndex: "field2",
  //             renderer: NOC.render.Bool
  //         }
  //     ]
  // })
  //
  Table: function(config){
    var fields = [],
      renderers = [],
      columns = config.columns || [],
      header = ["<div class='noc-tp'>", "<table>", "<tr>"];
    Ext.each(columns, function(c){
      fields.push(c.dataIndex || null);
      renderers.push(c.renderer || NOC.render.htmlEncode);
      header.push("<th>");
      header.push(Ext.util.Format.htmlEncode(c.text || ""));
      header.push("</th>");
    });
    header.push("</tr>");
    header = header.join("");
    return function(value){
      var r = [header];
      if(value){
        for(var i = 0; i < value.length; i++){
          var row = value[i];
          r.push("<tr>");
          for(var j = 0; j < fields.length; j++){
            r.push("<td>");
            r.push(renderers[j](row[fields[j]]));
            r.push("</td>");
          }
          r.push("</tr>");
        }
      } else{
        r.push("<tr><td></td></tr>");
      }
      r.push("</table>");
      return r.join("");
    }
  },

  JSON: function(v){
    if(!Ext.isEmpty(v)){
      return Ext.encode(v);
    }
  },

  Badge: function(v){
    if(v){
      return "<span class='x-display-tag'>" + v + "</span>";
    } else{
      return "";
    }
  },

  JobStatus: function(v){
    var map= {
      p: "<i class='fa fa-clock-o'></i> PENDING",
      w: "<i class='fa fa-pause'></i> WAITING",
      r: "<i class='fa fa-play'></i> RUNNING",
      S: "<i class='fa fa-stop'></i> SUSPENDED",
      s: "<i class='fa fa-check'></i> SUCCESS",
      f: "<i class='fa fa-exclamation-triangle'></i> FAILED",
      W: "<i class='fa fa-exclamation-circle'></i> WARNING",
      c: "<i class='fa fa-ban'></i> CANCELLED",
    };
    return map[v];
  },

  JobStatusIcon: function(v){
    var map = {
      p: ["clock-o", "Pending", NOC.colors.asbestos],
      w: ["pause-circle-o", "Waiting", NOC.colors.midnightblue],
      r: ["play-circle-o", "Running", NOC.colors.belizehole],
      S: ["stop-circle-o", "Suspended", NOC.colors.asbestos],
      s: ["check-circle-o", "Success", NOC.colors.yes],
      f: ["exclamation-triangle", "Failed", NOC.colors.no],
      W: ["exclamation-circle", "Warning", NOC.colors.pumpkin],
      c: ["ban", "Cancelled", NOC.colors.no],
    };
    var d = map[v];
    if(d === undefined){return "";}
    return '<i class="fa fa-' + d[0] + '" title="' + d[1] + '" style="color: ' + d[2] + '"></i>';
  },

  Subscribe: function(v, metaData){
    if(v === "no"){
      metaData.tdStyle = "cursor: not-allowed";
      return "<i class='fa fa-bell-slash x-action-col-icon' style='cursor: not-allowed'></i>";
    }
    if(v === "me"){
      return "<i class='fa fa-toggle-on x-action-col-icon'></i>";
    }
    if(v === "group"){
      return "<i class='fa fa-toggle-off x-action-col-icon'></i>";
    }
  },
});

//
Ext.apply(NOC.msg, {
  started: function(){
    Ext.toast({
      html: '<div style="text-align: center;"><i class="fa fa-clock-o" aria-hidden="true"></i>&nbsp' + Ext.String.format.apply(this, arguments) + "</div>",
      align: "bl",
      bodyStyle: {
        background: "#1E90FF",
        color: "white",
        "font-weight": "bold",
      },
      style: {
        background: "#1E90FF",
      },
      listeners: {
        focusenter: function(){
          this.close();
        },
      },
      width: "50%",
      minHeight: 10,
      paddingY: 0,
      border: false,
    });
  },
  complete: function(){
    Ext.toast({
      html: '<div style="text-align: center;"><i class="fa fa-check-circle" aria-hidden="true"></i>&nbsp' + Ext.String.format.apply(this, arguments) + "</div>",
      align: "bl",
      bodyStyle: {
        background: "green",
        color: "white",
        "font-weight": "bold",
      },
      style: {
        background: "green",
      },
      listeners: {
        focusenter: function(){
          this.close();
        },
      },
      width: "50%",
      minHeight: 10,
      paddingY: 0,
      border: false,
    });
  },
  failed: function(){
    Ext.toast({
      html: '<div style="text-align: center;"><i class="fa fa-bolt" aria-hidden="true"></i>&nbsp' + Ext.String.format.apply(this, arguments) + "</div>",
      align: "bl",
      bodyStyle: {
        background: "red",
        color: "white",
        "font-weight": "bold",
      },
      style: {
        background: "red",
      },
      listeners: {
        focusenter: function(){
          this.close();
        },
      },
      width: "50%",
      minHeight: 10,
      paddingY: 0,
      border: false,
    });
  },
  info_icon: function(icon){
    var args = Array.prototype.slice.call(arguments, 1);
    Ext.toast({
      html: '<div style="text-align: center;"><i class="fa ' + icon + ' " aria-hidden="true"></i>&nbsp' + Ext.String.format.apply(this, args) + "</div>",
      align: "bl",
      bodyStyle: {
        background: "#1E90FF",
        color: "white",
        "font-weight": "bold",
      },
      style: {
        background: "#1E90FF",
      },
      listeners: {
        focusenter: function(){
          this.close();
        },
      },
      width: "50%",
      minHeight: 10,
      paddingY: 0,
      border: false,
    });
  },
});

NOC.mrt = function(options){
  var offset = 0,
    rxChunk = /^(\d+)\|/,
    scope = options.scope,
    xhr = new XMLHttpRequest();

  scope.mask();
  // Start streaming request
  xhr.open(
    "POST",
    "/api/mrt/",
    true,
  );
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onprogress = function(){
    // Parse incoming chunks
    var ft = xhr.responseText.substr(offset),
      match, l, lh, chunk;

    while(ft){
      match = ft.match(rxChunk);
      if(!match){
        break;
      }
      lh = match[0].length;
      l = parseInt(match[1]);
      chunk = JSON.parse(ft.substr(lh, l));
      offset += lh + l;
      ft = ft.substr(lh + l);
    }
    if(!chunk.running){
      scope.unmask();
      options.cb(chunk.result, options.scope);
    }
  };
  xhr.send(JSON.stringify(options.params));
  xhr.onerror = function(){
    scope.unmask();
    NOC.error(__(options.errorMsg));
  };
};
//
NOC.error = function(){
  NOC.msg.failed.apply(this, arguments);
};
//
NOC.info = function(){
  NOC.msg.info_icon.apply(this, ["fa-info-circle", ...arguments]);
};
NOC.info_icon = function(){
  NOC.msg.info_icon.apply(this, arguments);
};
//
NOC.hasPermission = function(perm){
  return function(app){
    return app.hasPermission(perm);
  }
};
//
NOC.listToRanges = function(lst){
  var l = lst.sort(function(x, y){
      return x - y;
    }),
    lastStart = null,
    lastEnd = null,
    r = [],
    f = function(){
      if(lastStart == lastEnd){
        return lastStart.toString();
      } else{
        return lastStart.toString() + "-" + lastEnd.toString();
      }
    };

  for(var i = 0; i < l.length; i++){
    var v = l[i];
    if(lastEnd && (v == lastEnd + 1)){
      lastEnd += 1;
    } else{
      if(lastStart != null){
        r = r.concat(f());
      }
      lastStart = v;
      lastEnd = v;
    }
  }
  if(lastStart != null){
    r = r.concat(f());
  }
  return r.join(",")
};
//
//validate function def
//
NOC.is_vlanid = function(value){
  return (value >= 1 && value <= 4095)
};
//
NOC.is_asn = function(value){
  return (value > 0)
};
//
NOC.is_ipv4 = function(value){
  var arrayX = value.split("."),
    arrayoct = [];
  if(arrayX.length != 4)
    return false;
  else{
    for(var oct in arrayX){
      if((parseInt(arrayX[oct]) >= 0) && (parseInt(arrayX[oct]) <= 255))
        arrayoct.push(arrayX[oct]);
    }
    if(arrayoct.length != 4){
      return false;
    } else{
      return true;
    }
  }
};
//
NOC.is_ipv4_prefix = function(value){
  var arrayX = arrayX = value.split("/");
  if(arrayX.length != 2)
    return false;
  if(!NOC.is_ipv4(arrayX[0]))
    return false;
  if((parseInt(arrayX[1]) >= 0) && (parseInt(arrayX[1]) <= 32)){
    return true;
  } else{
    return false;
  }
};
//
// init quick labels for vtype validators
Ext.QuickTips.init();
Ext.form.Field.prototype.msgTarget = "side";

//
// Custom VTypes
//
Ext.define("NOC.form.field.VTypes", {
  override: "Ext.form.field.VTypes",

  // OID sensor checking
  SensorOID: function(val, field){
    var oidRegex = /^1\.3\.6(\.\d+)+$/;
    console.log(val, field);
    return oidRegex.test(val);
  },
  SensorOIDText: "Must be a OID",

  // VLAN ID checking
  VlanID: function(val){
    try{
      var id = parseInt(val);
      return NOC.is_vlanid(id);
    } catch(e){
      return false;
    }
  },
  VlanIDText: "Must be a numeric value [1-4095]",
  VlanIDMask: /[\d\/]/,

  // Autonomous system name checking
  ASN: function(val){
    try{
      var asn = parseInt(val);
      return NOC.is_asn(asn);
    } catch(e){
      return false;
    }
  },
  ASNText: "AS num must be a numeric value > 0",
  ASNMask: /[\d\/]/,

  // IPv4 check
  IPv4: function(val){
    try{
      return NOC.is_ipv4(val);
    } catch(e){
      return false;
    }
  },
  IPv4Text: "Must be a numeric value 0.0.0.0 - 255.255.255.255",
  IPv4Mask: /[\d\.]/i,
  // IPv4 check
  IPv4Group: function(val){
    if(val === "Leave unchanged") return true;
    try{
      return NOC.is_ipv4(val);
    } catch(e){
      return false;
    }
  },
  IPv4GroupText: "Must be a numeric value 0.0.0.0 - 255.255.255.255",
  IPv4GroupMask: /[\d\.]/i,

  // IPv4 prefix check
  IPv4Prefix: function(val){
    try{
      return NOC.is_ipv4_prefix(val);
    } catch(e){
      return false;
    }
  },
  IPv4PrefixText: "Must be a numeric value 0.0.0.0/0 - 255.255.255.255/32",
  IPv4PrefixMask: /[\d\.\/]/i,

  // FQDN check
  FQDN: function(val){
    var me = this;
    try{
      return me.FQDNRe.test(val);
    } catch(e){
      return false;
    }
  },
  FQDNRe: /^([a-z0-9\-]+\.)+[a-z0-9\-]+$/i,
  FQDNText: "Not valid FQDN",

  // AS-set check for compatibility whith: 
  //   https://apps.db.ripe.net/docs/08.Set-Objects/#creating-set-objects
  //   Valid:
  //     AS12345:AS-MEGA-2:AS-MEGA-3-SET
  //   Not valid:
  //     ASMEGA-2:AS-MEGA-3-SET 
  ASSET: function(val){
    var me = this;
    try{
      return me.ASSETRe.test(val);
    } catch(e){
      return false;
    }
  },
  ASSETRe: /^(AS-[\w-]+)|(AS\d+(:AS-[\w-]+)+)$/i,
  ASSETText: "Not valid AS or ASSET, must be in form AS3505, AS-SET, AS-MEGA-SET or AS3245:AS-TEST",

  // AS/AS-set check
  ASorASSET: function(val, field){
    var me = this;
    return me.ASN(val, field) || me.ASSET(val, field);
  },
  ASorASSETText: "Not valid AS or ASSET, must be in form AS3505, AS-SET, AS-MEGA-SET or AS3245:AS-TEST",

  // Color check
  color: function(val){
    var me = this;
    return me.colorRe.test(val);
  },
  colorRe: /^[0-9a-f]{6}$/i,
  colorText: "Invalid color, must be 6 hexadecimals",

  password: function(val, field){
    if(field.peerField){
      var form = field.up("form"),
        peer = form.getForm().findField(field.peerField);
      return (val === peer.getValue());
    }
    return true;
  },
  passwordText: "Passwords do not match",

  json: function(val){
    try{
      Ext.decode(val);
      return true
    } catch(err){
      return false;
    }
  },
  jsonText: "Invalid JSON",

  // Color check
  handler: function(val){
    var me = this;
    return me.handlerRe.test(val);
  },
  handlerRe: /^noc(\.[a-zA-Z_][a-zA-Z0-9_]*)+$/,
  handlerText: "Invalid handler format",

  float: function(val){
    return !isNaN(parseFloat(val))
  },
  floatText: "Invalid floating number",
});

//
// UI Styles
// Predefined set of size and settings.
// Applied to field as uiStyle property
//
NOC.uiStyles = function(style, theme){
  let convertToNoc = function(value){
      let grayLetter = 11,
        nocLetter = 16;
      if(theme === "noc"){
        value = value * nocLetter / grayLetter;
      }
      return Math.trunc(value);
    },
    baseWidth = convertToNoc(Ext.create("NOC.core.modelfilter.Base").width);
  
  switch(style){
    case "small": {
      // 3 letters 33px for gray theme, 1 letter 11px
      return {
        width: convertToNoc(55),
        anchor: null,
      }
    }
    case "medium": {
      // 20 letters
      return {
        width: baseWidth - convertToNoc(25),
        anchor: null,
      };
    }
    case "medium-combo": {

      return {
        width: baseWidth - convertToNoc(100),
        anchor: null,
      };
    }
    case "large": {
      // 40 letters
      return {
        width: baseWidth * 2,
        anchor: null,
      }
    }
    case "extra": {
      // Full width
      return {
        anchor: "100%",
      };
    }
  }
};
//
// https://docs.getnoc.com/<branch>/<language>/go.html#<имя ссылки>
//
NOC.openHelp = function(topic){
  var url, win;
  url = Ext.String.format(
    "{0}/{1}/{2}/go.html#{3}",
    NOC.settings.helpUrl,
    NOC.settings.helpBranch,
    NOC.settings.helpLanguage,
    topic,
  );
  win = window.open(url, "_blank");
  win.focus();
};

NOC.helpOpener = function(topic){
  return function(){
    NOC.openHelp(topic)
  }
};

NOC.clipboardIcon = function(value){
  return "<i class='fas fa fa-clipboard noc-to-clipboard' style='padding-left: 5px;cursor: pointer' title='"
      + __("Copy to clipboard") + "' onclick='NOC.toClipboard(\"" + value + "\")'></i>";
};

NOC.clipboard = function(value){
  if(!Ext.isEmpty(value)){
    return value + NOC.clipboardIcon(value);
  } 
  return value;
};
                  
NOC.toClipboard = function(text){
  navigator.clipboard.writeText(text)
  NOC.info(__("Copy to clipboard"));
};

NOC.saveAs = function saveFile(blob, filename){
  var url = window.URL.createObjectURL(blob),
    link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}