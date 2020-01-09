'use strict';
/**
 * Created by steveetm on 2017. 04. 08..
 */

// import { DirParser } from './DirParser';
let DirParser = require ('./DirParser');

const Promise = require('bluebird');
const fs = require('fs');

const cacheDir = './.cache';

class ExtParser {
    constructor(options) {
        this.options = options;
        this.classMap = null;
        try {
            fs.statSync(cacheDir);
        } catch(e) {
            fs.mkdirSync(cacheDir);
        }
        this.classMapPromise = this.getClassMap();
    }

    getClassMap() {
        let parseDir = new DirParser(this.options);
        const version = parseDir.readVersion();
        const cacheFile = cacheDir + '/' + version;
        if (fs.existsSync(cacheFile)) {
            const cachedResult = JSON.parse(fs.readFileSync(cacheFile, { encoding: 'utf-8' }));
            this.classMapCache = cachedResult.classMap;
            this.fileMapCache = cachedResult.fileMap;
            return Promise.resolve(cachedResult.classMap);
        } else {
            return parseDir.parse().then(() => {
                this.classMapCache = parseDir.classMap;
                this.fileMapCache = parseDir.fileMap;
                console.timeEnd('parsing vendor');
                fs.writeFileSync(cacheFile, JSON.stringify(parseDir));
                return Promise.resolve(parseDir.classMap);
            });
        }
    }

    ready() {
        return this.classMapPromise;
    }

    getClassMapCache() {
        if (this.classMapCache && this.classMapPromise.isFulfilled()) {
            return this.classMapCache;
        } else {
            throw new Error('Cannot use query while classMap is not initialized');
        }
    }

    query(className) {
        let obj = this.getClassMapCache();
        className.split('.').forEach((key) => {
            if (typeof obj === 'undefined') {
                return false;
            }
            if (key !== '*') {
                obj = obj[key];
            }

        });
        if (typeof obj === 'undefined') {
            return {};
        }
        let res = [];
        if (obj.classProp) {
            res.push(obj.classProp);
        }

        if (className.indexOf('*') > -1) {
            res.push(...Object.keys(obj).map((key) => {
                return this.query(className.replace('*', '') + key);
            }));
        }
        if (res.length === 1) {
            return res[0];
        } else {
            return res.filter((elem) => {
                return (Array.isArray(elem) && elem.length > 0) || (!Array.isArray(elem) && elem);
            });
        }

    }
}

module.exports = ExtParser;

// export { ExtParser };
