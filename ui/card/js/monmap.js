//----------------------------------------------------------------------
//  Monmap
//----------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//----------------------------------------------------------------------
var Monmap = function(){
  this.map = null;
  this.mapFilter = {statuses: [], isNotInit: true};
  this.refreshRange = 0;
  this.timeoutId = null;
};

Monmap.prototype.initialize = function(lon, lat, zoom){
  var q = this.parseQuerystring(),
    lon = q.lon ? parseFloat(q.lon) : lon || 135.656987,
    lat = q.lat ? parseFloat(q.lat) : lat || 55.005569,
    scale = q.zoom ? parseInt(q.zoom) : zoom || 5;
    // lon = q.lon ? parseFloat(q.lon) : lon || 37.5077,
    // lat = q.lat ? parseFloat(q.lat) : lat || 55.7766,
    // scale = q.zoom ? parseInt(q.zoom) : zoom || 11;
  this.objectId = (window.location.pathname.split("/").slice(-2))[0];
  this.map = L.map("map", {attributionControl: false});

  // Select view, trigger moveend to poll data
  this.map.setView([lat, lon], scale);

  settings = settingsLoader.run()

  mapLayersCreator.run(L, this, {
    default_layer: settings.gis.default_layer, 
    allowed_layers: settings.gis.base,
    yandex_supported: settings.gis.yandex_supported,
    layersControl: {"position": "bottomright"},
  });

  // Init markerCluster
  // doc: https://github.com/Leaflet/Leaflet.markercluster
  this.markerClusterGroup = L.markerClusterGroup({
    chunkedLoading: false,
    spiderfyDistanceMultiplier: 2.5,
    // spiderfyOnMaxZoom: false,
    // showCoverageOnHover: false,
    // zoomToBoundsOnClick: false,
    iconCreateFunction: function(cluster){
      var errors = cluster.getAllChildMarkers().reduce(function(a, b){
        return a + b.options.error
      }, 0);

      if(errors > 0){
        return new L.DivIcon({
          html: '<div><span>' + errors + '</span></div>',
          className: 'marker-cluster marker-cluster-error',
          iconSize: new L.Point(40, 40),
        });
      }

      var warnings = cluster.getAllChildMarkers().reduce(function(a, b){
        return a + b.options.warning
      }, 0);
      if(warnings > 0){
        return new L.DivIcon({
          html: '<div><span>' + warnings + '</span></div>',
          className: 'marker-cluster marker-cluster-warning',
          iconSize: new L.Point(40, 40),
        });
      }

      var maintenance = cluster.getAllChildMarkers().reduce(function(a, b){
        return a + b.options.maintenance
      }, 0);
      if(maintenance > 0){
        return new L.DivIcon({
          html: '<div><span>' + maintenance + '</span></div>',
          className: 'marker-cluster marker-cluster-maintenance',
          iconSize: new L.Point(40, 40),
        });
      }

      var goods = cluster.getAllChildMarkers().reduce(function(a, b){
        return a + b.options.good
      }, 0);
      return new L.DivIcon({
        html: '<div><span>' + goods + '</span></div>',
        className: 'marker-cluster marker-cluster-good',
        iconSize: new L.Point(40, 40),
      });
    },
  });
  this.poll_data();
};

Monmap.prototype.parseQuerystring = function(){
  var q = window.location.search.substring(1),
    vars = q.split("&"),
    r = {}, i, pair;
  for(i = 0; i < vars.length; i++){
    pair = vars[i].split("=");
    r[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1]);
  }
  return r;
};

Monmap.prototype.run = function(maintenance, lon, lat, zoom){
  this.maintenance = maintenance;
  this.initialize(lon, lat, zoom);
};

Monmap.prototype.poll_data = function(){
  var me = this;
  var bbox = me.map.getBounds(),
    w = bbox.getWest(),
    e = bbox.getEast(),
    n = bbox.getNorth(),
    s = bbox.getSouth(),
    zoom = me.map.getZoom();

  $("#summary").html('<i class="fa fa-spinner fa-spin"></i>' + "Loading ...");
  // $.getJSON("/ui/card/js/data.json")
  // .done(function(data) {              // test
  $.ajax("/api/card/view/monmap/ajax/?z=" + zoom + "&w=" + w + "&e=" + e + "&n=" + n + "&s=" + s + "&maintenance=" + me.maintenance + "&object_id=" + me.objectId)
    .done(function(data){
      // Init statuses
      if(me.mapFilter.isNotInit){
        me.mapFilter.isNotInit = false;
        me.mapFilter.statuses = $(data.summary).find('span')
            .map(function(){
              var id = $(this).attr('id');
              $(this).css("opacity", "1");
              return {id: id, value: "1", group: L.featureGroup.subGroup(me.markerClusterGroup)}
            }).get();
      } else{
        me.map.removeLayer(me.markerClusterGroup);
        me.markerClusterGroup.clearLayers();
        me.mapFilter.statuses
            .forEach(function(v){
              v.group.clearLayers();
            });
      }
      for(var i = 0; i < data.objects.length; i++){
        var a = data.objects[i];
        var color, fillColor;
        var link = "/api/card/view/object/" + a.id + "/";
        var text = "";
        if(typeof a !== 'undefined' && a.objects.length){
          var listLength = 10;
          var objects = a.objects.map(function(obj){
            var linkColor;
            if(obj.status === "error"){
              linkColor = "#FF0000";
            } else if(obj.status === "warning"){
              linkColor = "#F0C20C";
            } else if(obj.status === "maintenance"){
              linkColor = "#2032A0";
            } else{
              linkColor = "#6ECC39";
            }
            return '<li><a href="/api/card/view/managedobject/' + obj.id + '/" target="_blank" style="color: ' + linkColor + ';">'
                        + obj.name + '</a></li>'
          }).slice(0, listLength).join("");
          text += "<hr>Objects:<br><ul>" + objects + "</ul>";
          if(a.objects.length >= listLength){
            text += "<br><a href='" + link + "' target='_blank'>More...</a>";
          }
        }
        var title = "<a href='" + link + "' target='_blank'>" + a.name + "</a><br>good: " + a.good + "</br>error: " + a.error + "</br>warning: " + a.warning + text;
        var markerOptions = {
          title: title,
          error: a.error,
          warning: a.warning,
          good: a.good,
          maintenance: a.maintenance,
          fillOpacity: 0.6,
          opacity: 1,
          weight: 3,
        };

        if(a.error){
          color = "#FF0000";
          fillColor = "#FF4500";
        } else if(a.warning){
          color = "#F0C20C";
          fillColor = "#FFFF00";
        } else if(a.maintenance){
          color = "#2032A0";
          fillColor = "#87CEFA";
        } else{
          color = "#6ECC39";
          fillColor = "#B5E28C";
        }
        markerOptions.fillColor = fillColor;
        markerOptions.color = color;

        var marker = L.circleMarker(L.latLng(a.y, a.x), markerOptions);
        marker.bindPopup(title);
        // distribution by groups
        var statuses = [].concat.apply([], a.objects // flatMap
                .map(function(e){
                  return e.services
                }),
        )
            .filter(function(x, i, a){ // unique values
              return a.indexOf(x) === i;
            });
        statuses
            .forEach(function(statusId){
              var group;
              var groups = me.mapFilter.statuses
                .filter(function(e){
                  return e.id === statusId;
                });

              if(groups.length){
                group = groups[0].group;
              } else{
                var status = {id: statusId, value: "1", group: L.featureGroup.subGroup(me.markerClusterGroup)};
                group = status.group;
                me.mapFilter.statuses.push(status);
              }
              marker.addTo(group);
            });
      }
      me.mapFilter.statuses.forEach(function(value){
        value.group.addTo(me.map);
      });
      me.map.addLayer(me.markerClusterGroup);
      var summary = $('#summary');
      // Replace summary
      summary.html(data.summary);
      // Attach control
      summary.find("i,span").click(me, function(e){
        var opacity = $(this).css("opacity") || "1";
        var toggled = opacity === "1" ? "0.5" : "1";

        if($(this).prop("tagName") === "I"){
          e.data.filterByType($(this).attr('id'), toggled);
        } else{
          e.data.filterByStatus($(this).attr('id'), toggled);
        }

      });
      // Add refresh control
      var options = '<option value="0">Off</option><option value="300000">5 min</option><option value="600000">10 min</option><option value="900000">15 min</option><option value="1800000">30 min</option>';
      $('<label style="font-size: 20px" for="refreshRange">Refresh Time:&nbsp;</label><select style="font-size: 20px" id="refreshRange">' + options + '</select>')
        .appendTo(summary)
        .change(me, function(e){
          e.data.refreshRange = parseInt($(this).val(), 10);
          clearTimeout(e.data.timeoutId);
          e.data.poll_data();
        });
      $("#refreshRange").val(me.refreshRange);

      // restore status state
      if(!me.mapFilter.isNotInit){ // restore control state
        me.mapFilter.statuses.forEach(function(v){
          me.filterByStatus(v.id, v.value);
        });
        me.markerClusterGroup.refreshClusters();
      }
      clearTimeout(me.timeoutId);
      if(me.refreshRange){
        me.timeoutId = setTimeout(function(){
          me.poll_data();
        }, me.refreshRange);
      }
    });
};

Monmap.prototype.filterByType = function(typeId, value){
  var el = $("#" + typeId);

  $(el).css("opacity", value);
  $(el).parent().siblings().children().css("opacity", value);

  $(el).parent().siblings().children().get()
    .forEach(function(v){
      this.filterByStatus($(v).attr("id"), value);
    }, this);
  // Save control state
  this.mapFilter.statuses = this.mapFilter.statuses
    .map(function(v){
      if(v.id.indexOf(typeId + "-") === 0){
        v.value = value;
      }
      return v;
    });
};

Monmap.prototype.filterByStatus = function(statusId, value){
  var el = $("#" + statusId);
  var icon = $(el).parent().siblings().children("i");
  var iconOpacity = icon.css("opacity") || 1;
  var otherStatuses = $(el).parent().siblings().children("span")
    .map(function(){
      return $(this).css("opacity");
    }).get()
    .filter(function(e){
      return e !== value;
    }).length;

  $(el).css("opacity", value);
  if(!otherStatuses){
    icon.css("opacity", value);
  }

  if(value === "1" && iconOpacity === "0.5"){ // when one of statuses on and icon off
    icon.css("opacity", "1");
  }

  // Save control state
  this.mapFilter.statuses = this.mapFilter.statuses
    .map(function(v){
      if(v.id === statusId){
        v.value = value;
      }
      return v;
    });

  var groups = this.mapFilter.statuses.filter(function(e){
    return e.id === statusId;
  });
  if(groups.length > 0){
    if(value === '1'){
      groups[0].group.addTo(this.map);
    } else{
      // groups[0].group.removeFrom(this.map);
      this.mapFilter.statuses
            .forEach(function(value){
              value.group.removeFrom(this.map);
            }, this);

      var showGroups = this.mapFilter.statuses
            .filter(function(e){
              return e.value === "1"
            });
      if(showGroups.length){
        showGroups
                .forEach(function(value){
                  value.group.addTo(this.map);
                }, this);
      }
    }
  }
  this.markerClusterGroup.refreshClusters();
};
