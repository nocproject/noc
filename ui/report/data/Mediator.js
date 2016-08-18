// Generated by CoffeeScript 1.10.0
(function() {
  Ext.define('Report.data.Mediator', {
    singleton: true,
    sliceDateStream: function(from, to) {
      var ion;
      ion = Ext.create('Report.data.Ion', {
        method: 'sliceDateStream',
        data: {
          from: from,
          to: to
        },
        failure: this.standardErrorWindow,
        scope: this
      });
      return Report.data.Socket.send(ion);
    },
    bindModel: function(model, ionConfig) {
      return this.bindAnyStorage(function(data) {
        return model.set(data);
      }, ionConfig);
    },
    bindStore: function(store, ionConfig) {
      return this.bindAnyStorage(function(data) {
        return store.loadData(data);
      }, ionConfig);
    },
    connectToWellspring: function(ionConfig) {
      var ion;
      ion = Ext.create('Report.data.Ion', ionConfig);
      return Report.data.Socket.send(ion);
    },
    standardErrorWindow: function(error) {
      return Ext.Msg.show({
        icon: Ext.Msg.ERROR,
        title: 'Ошибка',
        message: error.toString(),
        buttons: Ext.Msg.OK
      });
    },
    privates: {
      bindAnyStorage: function(bindFn, ionConfig) {
        var originSuccess;
        originSuccess = ionConfig.success;
        ionConfig.success = function(data) {
          bindFn(data);
          return originSuccess != null ? originSuccess.apply(this, arguments) : void 0;
        };
        return this.connectToWellspring(ionConfig);
      }
    }
  });

}).call(this);

//# sourceMappingURL=Mediator.js.map
