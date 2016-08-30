Ext.define 'Report.data.AsyncInterface',

	config:
		success: Ext.emptyFn

		failure: Ext.emptyFn

		always: Ext.emptyFn

		scope: null

	constructor: (config) ->
		this.initConfig config
		@setScope @getScope or @

	callSuccess: () ->
		scope = @getScope()

		@getSuccess().apply scope, arguments
		@callAlways.apply scope, arguments

	callFailure: () ->
		scope = @getScope()

		@getFailure().apply scope, arguments
		@callAlways.apply scope, arguments

	callAlways: () ->
		@getAlways().apply @getScope(), arguments