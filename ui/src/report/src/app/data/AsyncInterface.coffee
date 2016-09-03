Ext.define 'Report.data.AsyncInterface',

  success: null

  failure: null

  always: null

  scope: null

  constructor: (config) ->
    scope = config.scope or @
    delete config.scope

    Ext.apply @, config

    setTimeout(
      () => @scope = scope
      0
    )

  callSuccess: (error, data) ->
    @success?.call @scope, data
    @callAlways.call @scope, error, data

  callFailure: (error, data) ->
    @failure?.call @scope, error
    @callAlways.call @scope, error, data

  callAlways: (error, data) ->
    @always?.call @scope, error, data