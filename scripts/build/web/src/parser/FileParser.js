/**
 * Parse Ext source files, gather JS annotations, fix invalid annotations.
 */
'use strict';

// import { TagParser } from './TagParser';
let TagParser = require('./TagParser');

let Promise = require('bluebird');
let Esprima = require('esprima');
let Path = require('path');
let readFile = Promise.promisify(require('fs').readFile);
let CommentParser = require('comment-parser');

const nameTags = ['define'];
const requireTags = ['require', 'mixins'];
const overrideTags = ['override'];

/**
 *
 * @property Array names
 * @property Array requires
 * @property Array override
 */

class FileParser {
    constructor(options = {}) {
        this.names = [];
        this.requires = [];
        this.override = "";
        this.ignoreOverrides = options.ignoreOverrides || false;
    }


    parse(src) {
        return this.loadFile(src)
        .then((content) => {
            return this.generateAST(content)
            .then((AST) => {
                return Promise.join(
                    this.extractComments(AST)
                    .then(this.groupComments.bind(this))
                    .then(this.parseTags.bind(this)),
                    this.extractCode(AST)
                )
            })
        })
    }

    generateAST(content) {
        return new Promise((resolve) => {
            return resolve(Esprima.parse(content.toString(), {
                tolerant: true,
                comment: true,
                tokens: false,
                range: false,
                loc: true
            }));
        });
    }

    /**
     * Loads a file and returns with the jsDoc comments
     *
     * @param src String
     */
    loadFile(src) {
        this.src = src;
        return readFile(Path.resolve(src))
        .then((content) => {
            return content.toString();
        });
    }

    addAlternateClassName() {
    }

    extractCode(AST) {
        let me = this;
        let esquery = require('esquery');
        const validDefines = `[expression.callee.object.name = 'Ext'][expression.callee.property.name = define][expression.arguments.0.value!='null']`;

        let matches = esquery.match(AST, esquery.parse(validDefines));
        if (matches && matches[0] && matches[0].expression.arguments) {
            me.addName(matches[0].expression.arguments[0].value);
        }

        matches = esquery.match(AST, esquery.parse(`${validDefines} ObjectExpression > Property[key.name=alternateClassName]`));
        if (matches && matches[0] && matches[0].value) {
            let node = matches[0].value;
            if (node.type === "Literal") {
                me.addName(node.value);
            } else if (node.type === "ArrayExpression") {
                node.elements.forEach((element) => {
                    me.addName(element.value);
                });
            }
        }
        matches = esquery.match(AST, esquery.parse(`${validDefines} ObjectExpression > Property[key.name=requires]`));
        if (matches && matches[0] && matches[0].value) {
            let node = matches[0].value;
            if (node.type === "Literal") {
                me.addRequire(node.value);
            } else if (node.type === "ArrayExpression") {
                node.elements.forEach((element) => {
                    me.addRequire(element.value);
                });
            }
        }
        if (!this.ignoreOverrides) {
            matches = esquery.match(AST, esquery.parse(`${validDefines} ObjectExpression > Property[key.name=override]`));
            if (matches && matches[0] && matches[0].value) {
                let node = matches[0].value;
                if (node.type === "Literal") {
                    me.addOverride(node.value);
                } else {
                    //console.log('found alternateClassName but not literal',matches);
                }
            }
        }

        return Promise.resolve();
    }

    /**
     * Return an
     *
     * @param AST
     * @returns {Promise.<Array>} Array of comment blocks
     */
    extractComments(AST) {

        return Promise.map(AST.comments, (comment) => {
            let value = comment.value;
            if (comment.type === 'Line') {
                value = `*${comment.value}`;
            }
            return CommentParser(`/*${value}*/`)[0];
        })
        .then(comments => comments.filter(Boolean))
    }

    /**
     * Gathers the tags from comment block and returns with the combined array of tags
     *
     * @param {Object[]} comments Array which contains the extracted comments
     * @param {String} comments[].tags Array of tags
     * @return Promise
     */
    groupComments(comments) {
        return Promise.reduce(comments, (ret, comment) => [...ret, ...comment.tags], []);
    }

    parseTags(tags) {
        return new Promise.each(tags, (tag) => {
            return this.parseTag(new TagParser(tag));
        });
    }

    parseTag(tag) {

        if (tag.tag === "class" && (tag.name === "Ext" || tag.name === "Ext.Widget")) {
            if (this.src.indexOf('Ext.js') === -1) {
                return Promise.resolve();
            }
        }

        if (nameTags.includes(tag.tag)) {
            this.addName(tag.name);
        }
        if (requireTags.includes(tag.tag)) {
            this.addRequire(tag.name);
        }
        if (overrideTags.includes(tag.tag)) {
            this.addOverride(tag.name);
        }
        /* if (tag.tag.indexOf('cmd-auto-dependency') > -1) {
             if (tag.type.defaultType && tag.type.defaultType.indexOf('Ext.') > -1) {
               console.log('Adding defaultType',tag.type.defaultType);
                 this.addRequire(tag.type.defaultType);
             }
         }*/
        return Promise.resolve();
    }

    addName(name) {
        if (name && name !== "" && !this.names.includes(name)) {
            this.names.push(name);
        }
    }

    addRequire(require) {
        this.requires.push(require);
    }

    addOverride(override) {
        this.override = override;
    }

}

// export { FileParser };
module.exports = FileParser;
