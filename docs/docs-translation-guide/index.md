# NOC Manual Translation

NOC uses [mkdocs-static-i18n][mkdocs-static-i18n] plugin
to translate the documentation.

## Adding Translation

NOC documentation is stored in the series of [Markdown][Markdown] files.
The translation is performed on the file-per-file basis.
The default language is english. To add a translation to file
`<name>.md` your should create file `<name>.<language code>.md`,
where `<language code>` is one of:

| Language | Code |
| -------- | ---- |
| Russian  | `ru` |

Then populate newly-created file with your translation.

## Localized Image

You can add un localized version of the images too,
just add the language code before an extension.

To localize `image.png` add `image.<laguage code>.png`.
Continue to refer an image in your traslated text
as `![...](image.png)`. The [mkdocs-static-i18n][mkdocs-static-i18n]
will resolve the name automatically.

## Contributing Work

After you have finished your work do not hesitate to share it
with the project by filling by creating Merge Request

!!! todo

    Add Link to Creating MR Guide

[Markdown]: https://www.markdownguide.org
[mkdocs-static-i18n]: https://github.com/ultrabug/mkdocs-static-i18n