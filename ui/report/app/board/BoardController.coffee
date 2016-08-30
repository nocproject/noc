Ext.define 'Report.board.BoardController',
	extend: 'Ext.app.ViewController'
	alias: 'controller.board'

	config:
		widgetLibraryWindow: null
		padding: 10
		cellHeight: 310
		columns: 4
		headerHeight: 56
		firstCall: true

		cursorSign: null
		matrix: null
		cursorMover: null
		filler: null

	constructor: () ->
		@callParent arguments

		@setCursorSign @makeNewCursor()
		@setMatrix @generateEmptyMatrix()
		@setCursorMover @makeCursorToFreeMover()
		@setFiller @makeFiller()

	showWidgetLibrary: () ->
		library = @getWidgetLibraryWindow()

		if not library
			library = @createWidgetLibrary()
			@setWidgetLibraryWindow library

		library.show()

	createWidgetLibrary: () ->
		Ext.create 'Report.library.Library',
			listeners:
				addWidget: 'addWidget'

	addWidget: (library, model) ->
		#TODO

	dotting: () ->
		items = @getItems()
		cursor = @makeNewCursor()
		matrix = @generateEmptyMatrix()
		cursorMove = @makeCursorToFreeMover matrix, cursor
		populate = @makeFiller matrix, cursor

		for item in items

			width = item.boardWidth
			height = item.boardHeight

			cursorMove width
			populate width, height

			@setItemSize item, width, height
			@moveItem(
				@positioning cursor, width
				item
			)

	privates:

		generateEmptyMatrix: () ->
			matrix = []

			for column in [0...@getColumns()]
				matrix.push []

				for cell in [0...100]
					matrix[column][cell] = false

			return matrix

		makeNewCursor: () ->
			{
				col: 0
				row: 0
			}

		getItems: () ->
			@getView().query('widgetBase')

		getWidth: () ->
			@getView().getWidth()

		getColWidth: () ->
			@getWidth() / @getColumns()

		positioning: (cursor, width) -> (item) =>
			x = @calcX cursor.col, width
			y = @calcY cursor.row

			@toEndOfTurn () =>
				item.setLocalXY(x, y)
				item.on 'move', @dotting, @, {single: true}

				@dottingAgainIfFirstCall()

		toEndOfTurn: (fn) ->
			setTimeout fn, 0

		calcX: (col, width) ->
			@getColWidth() * (col - width) + @getPadding()

		calcY: (row) ->
			@getCellHeight() * row - @getHeaderHeight() * row + @getDoublePadding()

		dottingAgainIfFirstCall: () ->
			if @getFirstCall
				@setFirstCall false
				@dotting()

		moveItem: (move, item) ->
			if item.rendered
				move item
			else
				item.on 'afterrender', move, @

		getDoublePadding: () ->
			@getPadding() * 2

		getMagicHeightPadding: () ->
			@getPadding() * 7.5

		setItemSize: (item, width, height) ->
			@setItemWidth item, width
			@setItemHeight item, height

		setItemWidth: (item, width) ->
			item.setWidth @calcItemWidth width

		calcItemWidth: (width) ->
			width * @getColWidth() - @getDoublePadding()

		setItemHeight: (item, height) ->
			item.setHeight @calcItemHeight height

		calcItemHeight: (height) ->
			total = height * @getCellHeight()
			header = @getHeaderHeight() * (height - 1)
			padding = @getMagicHeightPadding()

			total - header - padding

		makeCursorToFreeMover: () -> (width) ->
			matrix = @getMatrix()
			cursor = @getCursorSign()

			loop
				overflow = @isOverflow cursor, width
				engaged = @isEngaged matrix, cursor

				if overflow or engaged
					@nextRow cursor
				else
					break

		isOverflow: (cursor, width) ->
			cursor.col + width > @getColumns()

		isEngaged: (matrix, cursor) ->
			matrix[cursor.col][cursor.row]

		nextRow: (cursor) ->
			cursor.col = 0
			cursor.row = cursor.row + 1

		makeFiller: (А) -> (width, height) =>
			matrix = @getMatrix()
			cursor = @getCursorSign()

			for colIndex in [0...width]
				col = cursor.col + colIndex
				row = cursor.row

				matrix[col][row] = true

				for rowIndex in [0...height]
					row = cursor.row + rowIndex

					matrix[col][row] = true