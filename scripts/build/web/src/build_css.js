const fs = require('fs');
const loaderJS = require('./loader');
const postcss = require('postcss');
// processors
const atImport = require('postcss-import');
const mqpacker = require('css-mqpacker');
const cssnano = require('cssnano');
// const autoprefixer = require('autoprefixer');
const url = require('postcss-url');

const sha1 = loaderJS.sha1;
const bundleName = 'app';

const build = function(destDir, themes) {
    function _build(destDir, theme) {
        const source = 'src/application.css';
        const prodName = `${destDir}/${bundleName}.{hash}.${theme}.css`;
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
        const content = fs.readFileSync(source);

        return new Promise((resolve, reject) => {
            postcss(processors)
            .process(content.toString().replace(/{theme-name}/g, theme), {from: source, to: prodName})
            .then(result => {
                const hash = sha1(result.css);
                fs.writeFile(prodName.replace(/{hash}/, hash), result.css,
                    err => {
                        if(err) {
                            reject(err);
                            return false;
                        }
                        // ToDo make map
                        // if(result.map) {
                        //     fs.writeFileSync(`${prodName}.map`, result.map);
                        // }
                        resolve({name: `${bundleName}.{hash}`, theme: theme, hash: hash});
                        return true;
                    });
            })
        });
    }

    return themes.map(theme => _build(destDir, theme));
};
module.exports = build;
