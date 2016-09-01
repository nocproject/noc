Ext.define 'Report.data.Socket',
	singleton: true

	url: '/api/bi/'
	curId: 0

	send: (ion) ->
		return if ion.destroyed

		@prepareIon ion
		@sendRequest ion

	getId: () ->
		@curId = ++@curId

	privates:

		prepareIon: (ion) ->
			ion.body ?= {}

			ion.body = Ext.apply ion.body, {
				id: @getId()
				jsonrpc: '2.0'
			}

		sendRequest: (ion) ->
			ion.pending = true

			data = Ext.clone ion.body
			data.params = ion.params

			Ext.create('Ext.data.Connection').request {
				url: @url
				jsonData: data
				callback: (opt, success, response) =>
					@handleResponse ion, success, response
			}

		handleResponse: (ion, success, response) ->
			return if ion.destroyed

			ion.pending = false

			unless success
				ion.error = 'Request error'
				ion.callCallback()
				return

			data = Ext.JSON.decode response.responseText, true

			unless data
				ion.error = 'Cant parse response'
				ion.callCallback()
				return

			if data.error
				ion.error = data.error
				ion.callCallback()
				return

			ion.result = data.result
			ion.isSuccess = true
			ion.callCallback()

