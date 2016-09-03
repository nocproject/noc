Ext.define 'Report.data.Ion',
  extend: 'Report.data.AsyncInterface'

# Server method to call
  method: ''

# Params for server
  params: null

# Result data or null if error
  result: null

# Error text or null
  error: ''

# Success request flag
  isSuccess: false

# Pending flag
  pending: false

# Request body params
  body: null

  callSuccess: () ->
    @callParent [@error, @result]

  callFailure: () ->
    @callParent [@error, @result]

  callCallback: () ->
    if @isSuccess
      @callSuccess
    else
      @callFailure