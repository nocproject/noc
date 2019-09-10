const loader = require('./loader');
const UglifyJS = require("uglify-js");
const fs = require('fs');
const apps = require('./applications');

const cache = [];
const bundleName = 'bundle';
const devName = `${bundleName}.js`;
const prodName = `${bundleName}.min.js`;
let bundle = fs.openSync(devName, 'w');

function appendFile(file) {
    console.log(`append file : ${file}`);
    let content = fs.readFileSync(file);
    fs.appendFileSync(devName, content);
}

apps.forEach(filename => {
    let requires = loader(filename);
    requires.order.forEach(file => {
        if(!cache.includes(file)) {
            cache.push(file);
        }
    });
});

cache.forEach(file => {
    appendFile(file);
});
console.log(`Cache size is ${cache.length} file(s)`);
fs.closeSync(bundle);

const code = fs.readFileSync(devName, "utf8");

bundle = fs.openSync(prodName, 'w');
fs.appendFileSync(prodName, UglifyJS.minify(code).code);
fs.closeSync(bundle);
