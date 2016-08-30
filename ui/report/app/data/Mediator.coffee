Ext.define 'Report.data.Mediator',
	singleton: true

	sliceDateStream: (from, to) ->
		ion = Ext.create 'Report.data.Ion',
			method: 'sliceDateStream'
			data: {
				from
				to
			}
			failure: @standardErrorWindow
			scope: @

		Report.data.Socket.send ion

	bindModel: (model, ionConfig) ->
		@bindAnyStorage(
			(data) -> model.set data
			ionConfig
		)

	bindStore: (store, ionConfig) ->
		@bindAnyStorage(
			(data) -> store.loadData data
			ionConfig
		)

	connectToWellspring: (ionConfig) ->
		ion = Ext.create 'Report.data.Ion', ionConfig

		Report.data.Socket.send ion

	standardErrorWindow: (error) ->
		Ext.Msg.show {
			icon: Ext.Msg.ERROR
			title: 'Ошибка'
			message: error.toString()
			buttons: Ext.Msg.OK
		}

	privates:

		bindAnyStorage: (bindFn, ionConfig) ->
			originSuccess = ionConfig.success

			ionConfig.success = (data) ->
				bindFn data
				originSuccess?.apply @, arguments

			@connectToWellspring ionConfig