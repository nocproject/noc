//---------------------------------------------------------------------
// NOC.core.ConnectionGraph
// utility class for building and analyzing port connection graph
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ConnectionGraph");

Ext.define("NOC.core.ConnectionGraph", {
  singleton: true,
  graph: null,

  initGraph: function(){
    this.graph = {
      adjacencyList: new Ext.util.HashMap(),
            
      addVertex: function(vertex){
        if(!this.adjacencyList.containsKey(vertex.id)){
          this.adjacencyList.add(vertex.id, {
            connections: [],
            labels: [],
            data: vertex,
          });
        }
      },
            
      addEdge: function(from, to){
        this.addVertex(from);
        this.addVertex(to);
        this.adjacencyList.get(from.id).connections.push(to.id);
        this.adjacencyList.get(to.id).connections.push(from.id);
        if(!Ext.isEmpty(from.discriminator)){
          this.adjacencyList.get(from.id).labels.push(from.discriminator);
        }
        if(!Ext.isEmpty(to.discriminator)){
          this.adjacencyList.get(to.id).labels.push(to.discriminator);
        }
      },
            
      getPorts: function(){
        const connections = [];
          
        this.adjacencyList.each(function(key, value){
          connections.push({
            id: value.data.id,
            connectionCount: value.connections.length,
            labels: value.labels,
          });
        });
        return connections;
      },
      
      getConnections: function(){
        const connections = [];
        this.adjacencyList.each(function(fromId, fromValue){
          fromValue.connections.forEach(function(toId){
            if(fromId < toId){
              connections.push({
                from: fromValue.data,
                to: this.adjacencyList.get(toId).data,
              });
            }
          }, this);
        }, this);
        return connections;
      },

      getPortsWithManyLabel: function(){
        const ports = [];
        this.adjacencyList.each(function(key, value){
          if(value.labels.length > 1){
            ports.push({
              id: value.data.id,
              connections: value.connections,
              labels: value.labels,
            });
          }
        });
        return ports;
      },
    };
  },

  buildGraphFromConnections: function(connections){
    this.initGraph();
        
    Ext.Array.each(connections, function(connection){
      this.graph.addEdge(connection.from, connection.to);
    }, this);
  },

  getConnections: function(){
    return this.graph ? this.graph.getConnections() : [];
  },
    
  getPorts: function(){
    return this.graph ? this.graph.getPorts() : [];
  },

  getPortsWithManyLabel: function(){
    return this.graph ? this.graph.getPortsWithManyLabel() : [];
  },
});