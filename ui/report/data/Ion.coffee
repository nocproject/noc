Ext.define 'Report.data.Ion',
	extend: 'Report.data.AsyncInterface'

	config:
		method: ''
		data: null
		autoDestroy: true

	callAlways: () ->
        @callParent arguments

        if @getAutoDestroy() then @destroy()