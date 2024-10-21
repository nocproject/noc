//---------------------------------------------------------------------
// NOC.core.mixins.Export
// export array of objects to csv
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.mixins.Export");

Ext.define("NOC.core.mixins.Export", {
  /**
     * Converts an array of objects (with identical schemas) into a CSV table.
     * @param {Array} objArray An array of objects.  Each object in the array must have the same property list.
     * @param {string} sDelimiter The string delimiter.  Defaults to a double quote (") if omitted.
     * @param {string} cDelimiter The column delimiter.  Defaults to a comma (,) if omitted.
     * @return {string} The CSV equivalent of objArray.
     */
  toCsv: function(objArray, sDelimiter, cDelimiter){
    var i, l, names = [], name, value, obj, row, output = "", n, nl;

    function toCsvValue(theValue, sDelimiter){
      var t = typeof (theValue), output;
      if(typeof (sDelimiter) === "undefined" || sDelimiter === null){
        sDelimiter = '"';
      }
      if(t === "undefined" || t === null){
        output = "";
      } else if(t === "string"){
        output = sDelimiter + theValue + sDelimiter;
      } else if(Ext.isArray(theValue)){
        output = sDelimiter + theValue.join(" ") + sDelimiter;
      } else{
        output = String(theValue);
      }
      return output;
    }

    // Initialize default parameters.
    if(typeof (sDelimiter) === "undefined" || sDelimiter === null){
      sDelimiter = '"';
    }
    if(typeof (cDelimiter) === "undefined" || cDelimiter === null){
      cDelimiter = ",";
    }
    for(i = 0, l = objArray.length; i < l; i += 1){
      // Get the names of the properties.
      obj = objArray[i];
      row = "";
      if(i === 0){
        // Loop through the names
        for(name in obj){
          if(Object.prototype.hasOwnProperty.call(obj, name)){
            names.push(name);
            row += [sDelimiter, name, sDelimiter, cDelimiter].join("");
          }
        }
        row = row.substring(0, row.length - 1);
        output += row;
      }
      output += '\n';
      row = "";
      for(n = 0, nl = names.length; n < nl; n += 1){
        name = names[n];
        value = obj[name];
        if(n > 0){
          row += ","
        }
        row += toCsvValue(value, '"');
      }
      output += row;
    }
    return output;
  },

  export: function(records, columns){
    var out = [];

    Ext.Array.forEach(records, function(item){
      var record = {};
      Ext.Array.forEach(this.columns, function(column){
        if(column.dataIndex){
          var index = column.dataIndex;
          if((index + '__label') in this.item.data){
            index += '__label';
          }
          if(index === 'labels'){
            this.record[column.dataIndex] = Ext.Array.map(this.item.get(index), function(label){return label.id}).join(',');
          } else{
            this.record[column.dataIndex] = this.item.get(index);
          }
        }
      }, {item: item, record: record});
      this.out.push(record);
      item.get(this.columns[0].dataIndex)
    }, {columns: columns, out: out});
    return this.toCsv(out);
  },

  save: function(grid, filename, cols){
    var records, columns;

    try{
      if('NOC.core.ModelStore' === Ext.getClassName(grid.getStore())){
        var renderPlugin = grid.findPlugin('bufferedrenderer'),
          first = renderPlugin.getFirstVisibleRowIndex(),
          last = renderPlugin.getLastVisibleRowIndex();

        records = grid.getStore().getRange(first, last);
      } else{
        records = grid.getStore().getRange(0);
      }
      if(cols){
        columns = cols;
      } else{
        columns = grid.getVisibleColumns();
      }
    } catch(e){
      return false;
    }

    var blob = new Blob([this.export(records, columns)], {type: "text/plain;charset=utf-8"});
    this.downloadCsv(blob, filename);
  },

  downloadCsv: function(blob, filename){
    saveAs(blob, filename);
  },
});