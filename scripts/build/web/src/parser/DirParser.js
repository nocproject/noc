'use strict';
/**
 * Parse Ext source directory.
 */
let FileParser = require('./FileParser');
let Path = require('path');
let Glob = require('glob');
let Promise = require('bluebird');

class DirParser {
    /**
     *
     *
     * @param {Object} options
     * @param {String} options.path
     * @param {String} options.toolkit
     * @param {String[]} options.packages
     *
     */
    constructor(options) {
        this.fileMap = options.fileMap || {};
        this.classMap = options.classMap || {};
        this._path = options.path;
        try {
            let packageJson = require(this.getPath() + '/package.json');
            packageJson = packageJson.sencha || packageJson;
            this.type = packageJson.type;
            // this.packageJson = packageJson;
            if (packageJson.classpath && packageJson.type !== 'framework') {
                if (typeof packageJson.classpath == 'string') {
                    this.classPath = Path.normalize(packageJson.classpath.replace('${package.dir}', this.getPath()));
                } else {
                    this.classPath = packageJson.classpath.map((path) => {
                        return path.replace('${package.dir}', this.getPath()).replace('${toolkit.name}', options.toolkit);
                    });
                }
            } else {
                this.classPath = Path.normalize(this.getPath() + '');
            }
            this.namespace = options.namespace || packageJson.namespace || "Ext";
            // this.namespace.toUpperCase() + this.namespace.slice(1, this.namespace.length)
            this.packages = [...options.packages ? options.packages : []];
            this.toolkit = options.toolkit;
        } catch (e) {
            console.error('error', e);
            throw new Error(e);
        }
        this.toolkit = options.toolkit;
    }

    readVersion() {
        var pjson = require(this.getPath() + '/package.json');
        console.log(pjson.version);
        return pjson.version;
    }

    getPath() {
        let ExpandTilde = require('expand-tilde');
        return Path.resolve(ExpandTilde(Path.normalize(this._path)));
    }

    normalizeClass(file) {
        return this.namespace + file.replace(this.classPath, '').replace(/\//g, '.').replace('.js', '');
    }

    createNS(className) {
        let obj = this.classMap;
        className.split('.').forEach(key => {
            if (key !=='*') {
                obj = obj[key] = obj[key] || {};
            }
        });
        return obj;
    }

    getNS(className) {
        let objValue = this.classMap;
        className.split('.').forEach((key) => {
            objValue = objValue[key];
        });
        return objValue;
    }

    saveClass(className, file) {
        let objValue =  this.createNS(className);
        objValue.classProp = this.fileMap[file];
        objValue.classProp.src = file;
        objValue.classProp.overrides = [];

    }

    saveOverride(override, file) {
        if (override.length === 0) {
            return;
        }
        let obj = this.createNS(override);
        if (obj.classProp) {
            obj.classProp.overrides.push(file);
        }
    }

    parse() {
        return this.processPackages(this.packages)
        .then(() => {
            return this.processToolkit(this.toolkit)
        })
        .then(this.processDir.bind(this))

    }

    processPackages(packages) {
        let path = this.classPath;
        return new Promise.each(packages, (req) => {
            let dirParser = new DirParser({
                path: path + '/packages/' + req,
                // path: path + '/' + req,
                toolkit: this.toolkit,
                classMap: this.classMap,
                fileMap: this.fileMap
            });
            return dirParser.parse().then(() => {
                Object.assign(this.fileMap, dirParser.fileMap);
                Object.assign(this.classMap, dirParser.classMap);
            });
        });
    }

    processToolkit(toolkit) {
        let path = this.classPath;
        if (this.type !== 'framework') {
            return Promise.resolve(this.classMap);
        }

        let dirParser = new DirParser({
            path: path + '/' + toolkit + '/' + toolkit,
            toolkit: this.toolkit,
            fileMap: this.fileMap,
            classMap: this.classMap
        });
        return dirParser.parse().then(() => {
            Object.assign(this.fileMap, dirParser.fileMap);
            return Object.assign(this.classMap, dirParser.classMap);
        });

    }

    processDir() {
        switch (this.type) {
            case 'framework' :
                break;
            /* let dirParser = new DirParser({
             path: `${this.getPath()}/${this.toolkit}/${this.toolkit}`,
             toolkit: this.toolkit
             });
             return dirParser.parse().then(() => {
             Object.assign(this.fileMap, dirParser.fileMap);
             return Object.assign(this.classMap, dirParser.classMap);
             });
             break;*/
            case 'toolkit' :
                return this.processPackage();
            case 'code' :
                return this.processPackage();
        }

    }

    processPackage() {
        return new Promise((resolve) => {
            return this.processSrc()
            .then(this.processOverride.bind(this))
            .then(resolve);
        });
    }

    processSrc() {
        return new Promise((resolve, reject) => {
            (Array.isArray(this.classPath) ? this.classPath : [this.classPath])
            .forEach((path) => {
                Glob(path + '/**/*.js', {}, (err, files) => {
                    if (err) {
                        return reject(err);
                    }
                    Promise.each(files, (file) => {
                        return this.processFile(file);
                    }).then(resolve);
                });
            });
        });
    }

    processOverride() {
        return new Promise((resolve, reject) => {
            Glob(this.classPath + '/../overrides/**/*js', {}, (err, files) => {
                if (err) {
                    return reject(err);
                }
                Promise.each(files, (file) => {
                    return this.processFile(file);
                }).then(resolve);
            });
        });
    }

    processFile(file) {
        let parser = new FileParser({
            ignoreOverrides: this.namespace.toLowerCase() === 'deft'
        });
        return parser.parse(file).then(() => {
            this.fileMap[file] = {
                names: parser.names,
                requires: parser.requires,
                override: parser.override
            };
            parser.names.forEach((className) => {
                this.saveClass(className, file);
            });
            this.saveClass(this.normalizeClass(file), file);
            this.saveOverride(parser.override, file);
        });
    }
}

module.exports = DirParser;
