Ext.define 'Report.board.MenuController',
	extend: 'Ext.app.ViewController'
	alias: 'controller.boardMenu'

	currentDay: () ->
		@sliceTo new Date

	yesterday: () ->
		@sliceToMargin 'DAY', 1

	week: () ->
		@sliceToMargin 'DAY', 7

	month: () ->
		@sliceToMargin 'MONTH', 1

	quarter: () ->
		@sliceToMargin 'MONTH', 3

	year: () ->
		@sliceToMargin 'YEAR', 1

	dateFrom: (widget, value) ->
		@slice value, @toFieldValue()

	dateTo: (widget, value) ->
		@slice @fromFieldValue(), value

	addWidget: () ->
		@getView().fireEvent 'addWidget', @

	privates:

		sliceToMargin: (type, count) ->
			@sliceTo @dateMargin type, count

		sliceTo: (to) ->
			@slice new Date, to

		slice: (from, to) ->
			Report.data.Mediator.sliceDateStream from, to

			@fromField().setValue from
			@toField().setValue to

		fromFieldValue: () ->
			@fromField().getValue() or new Date

		toFieldValue: () ->
			@toField().getValue() or new Date

		fromField: () ->
			@getView().down '#from'

		toField: () ->
			@getView().down '#to'

		dateMargin: (type, count) ->
			Ext.Date.add new Date, Ext.Date[type], -count