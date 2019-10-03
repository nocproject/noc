const fs = require('fs');
const postcss = require('postcss');
// processors
const atImport = require('postcss-import');
const mqpacker = require('css-mqpacker');
const cssnano = require('cssnano');
// const autoprefixer = require('autoprefixer');
const url = require('postcss-url');

const bundleName = 'bundle_app';

const build = function(destDir, themes) {
    function _build(destDir, theme) {
        const source = 'src/application.css';
        const prodName = `${destDir}/${bundleName}_${theme}.min.css`;
        const processors = [
            atImport,
            // autoprefixer,
            mqpacker,
            url(
                {
                    url: 'inline'
                }
            ),
            cssnano
        ];
        fs.readFile(source, (err, css) => {
            postcss(processors)
            .process(css.toString().replace(/{theme-name}/g, theme), {from: source, to: prodName})
            .then(result => {
                fs.writeFile(prodName, result.css, () => true);
                if(result.map) {
                    fs.writeFile(`${prodName}.map`, result.map, () => true)
                }
            })
        });
    }

    themes.forEach(theme => _build(destDir, theme));
};
module.exports = build;
