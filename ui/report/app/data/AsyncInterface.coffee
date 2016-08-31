Ext.define 'Report.data.AsyncInterface',

	success: null

	failure: null

	always: null

	scope: null

	constructor: (config) ->
		this.initConfig config
		@scope ?= @

	callSuccess: (error, data) ->
		@success?.call @scope, data
		@callAlways.call @scope, error, data

	callFailure: (error, data) ->
		@failure?.call @scope, error
		@callAlways.call @scope, error, data

	callAlways: (error, data) ->
		@always?.call @scope, error, data