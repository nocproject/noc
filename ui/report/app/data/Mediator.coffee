Ext.define 'Report.data.Mediator',
	singleton: true

	sliceDateStream: (from, to) ->
		ion = Ext.create 'Report.data.Ion',
			method: 'sliceDateStream'
			params: [from, to]
			failure: @showStandardErrorWindow
			scope: @

		Report.data.Socket.send ion

	updateModel: (model, ion) ->
		@updateAnyStorage(
			(data) -> model.set data
			ion
		)

	updateStore: (store, ion) ->
		@updateAnyStorage(
			(data) -> store.loadData data
			ion
		)

	showStandardErrorWindow: (error) ->
		Ext.Msg.show {
			icon: Ext.Msg.ERROR
			title: 'Ошибка'
			message: error
			buttons: Ext.Msg.OK
		}

	privates:

		updateAnyStorage: (fn, ion) ->
			ion = @prepareIon ion
			originSuccess = ion.success

			ion.success = (data) ->
				fn data
				originSuccess?.apply @, arguments

			Report.data.Socket.send ion

		prepareIon: (ion) ->
			unless ion instanceof Report.data.Ion
				ion = Ext.create 'Report.data.Ion', ion

			unless ion.failure
				ion.failure = @showStandardErrorWindow

			ion