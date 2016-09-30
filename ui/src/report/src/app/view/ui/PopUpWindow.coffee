###
    Окно с анимацией появления.
###
Ext.define 'Report.view.ui.PopUpWindow',
	extend: 'Ext.window.Window'
	
	constructor: () ->
		@width /= 2
		@height /= 2
		
		@callParent arguments
	
	listeners:
	
		show: () ->
			@animate {
				to:
					x: @getX() - @getWidth() / 2
					y: @getY() - @getHeight() / 2
					width: @getWidth() * 2
					height: @getHeight() * 2
			}
	
		beforehide: () ->
			opacity = Number @getEl().getStyle('opacity')
			
			unless opacity then return true
			
			@animate {
				to:
					y: @getY() + 200
					opacity: 0
			}
			
			setTimeout(
				() => @hide()
				1000
			)
			
			false