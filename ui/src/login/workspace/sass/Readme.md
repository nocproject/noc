# ./sass

This folder contains the styling for the application's views.

## Styling

Sencha Cmd supports styling using Sass and integrates the styling from the theme
and required packages (specified in `"app.json"`) with application-defined views.

### ./sass/etc

This folder contains misc. support code for Sass builds (global functions, etc.).

### ./sass/src

This folder contains Sass files defining CSS rules corresponding to classes
included in the application's JavaScript code build. By default, files in this 
folder are mapped to the application's root namespace, 'NOC.login'. This is set in
`"app.json"`:

    "sass": {
        "namespace": "NOC.login"
    }

### ./sass/var

This folder contains Sass files defining Sass variables corresponding to classes
included in the application's JavaScript code build. By default, files in this 
folder are mapped to the application's root namespace, 'NOC.login' in the same way
as `"NOC.login/sass/src"`.

## Slicing

Internet Explorer 8 and 9 do not support linear gradients and IE8 does not support
border-radius. To compensate for this, Sencha Cmd provides "image slicing" using an
internal WebKit based renderer. To enable this, there is a special web page that
renders all components and states so they can be captured and turned into image
sprites.

### ./sass/example

This folder contains the web page used to present all components and states so they
can be captured as an image and used to produce images for IE8 and 9.

This web page is also helpful when loaded in Chrome to view all components in their
styled form.
