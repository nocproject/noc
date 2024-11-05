const esprima = require('esprima');
const esUtils = require('esprima-ast-utils');
const chalk = require('chalk');
const crypto = require("crypto");
const fs = require('fs');

const cacheDir = './.cache';

const sha1 = function(data) {
    return crypto.createHash("sha1").update(data).digest("hex");
};

const parse = function(entry) {
    const query = {
        sourceMap: false,
        debug: false,
        nameSpace: 'NOC',
        paths: {
            'Ext.ux': '../../../ui/web/ux',
            NOC: '../../../ui/web',
        }
    };
    const configMap = {
        requires: true,
        model: true,
        mixins: {
            allowObject: true
        },
        override: true,
        extend: true,
        uses: true,
        stores: {
            prefix: query.nameSpace + '.store.'
        },
        controllers: {
            prefix: query.nameSpace + '.controller.'
        },
        controller: true
    };
    const properties = Object.keys(configMap);
    const notFound = new Set();
    let debug = query.debug;
    let pathMap = query.paths || {};
    let root = {name: entry, children: []};

    /**
     * Resolve the given className as a path using the options->paths mapping defined in the config
     *
     * @param className
     * @returns {*}
     */
    function resolveClassFile(className) {
        let retVal = [];
        for(const prefix in pathMap) {
            let re = new RegExp('^' + prefix);
            if(className.match(re)) {
                if(pathMap[prefix] === false) {
                    retVal = [];
                } else {
                    if(typeof pathMap[prefix].query === 'function') {
                        let classes = pathMap[prefix].query(className);
                        if(classes instanceof Array) {
                            retVal = classes.map((className) => {
                                return className.src
                            });
                        } else {
                            try {
                                retVal = [classes.src, ...classes.overrides];
                            } catch(e) {
                                notFound.add(className);
                                console.warn('not found :', prefix, className);
                            }
                        }
                    } else {
                        retVal = [prefix.replace(prefix, pathMap[prefix]) + className.replace(prefix, '').replace(/\./g, '/') + '.js'];
                    }
                }
                break;
            }
        }
        return [...retVal];
    }

    function getRequireFile(className, prefix) {
        const r = new Set();
        if(className.indexOf('.') > 0 || prefix !== '' || className === 'Ext') {
            let fileToRequire = resolveClassFile(((className.indexOf('.') > 0) ? '' : prefix) + className);
            if(fileToRequire.length > 0) {
                fileToRequire.forEach((req) => {
                    if(debug) console.log(chalk.green('Converting require: ') + className + ' => ' + req);

                    if(typeof req === 'undefined') {
                        console.log(chalk.red('Converting require: ') + className + ' => ' + req);
                    }
                    // r.add(escodegen.generate({type: 'Literal', value: req}));
                    r.add(req);
                });
            }
        }
        return r;
    }

    /**
     * Make cache directory
     */
    try {
        fs.statSync(cacheDir);
    } catch(e) {
        fs.mkdirSync(cacheDir);
    }

    function makeGraph({name: filename, children: children}, level, vertexes, edges) {
        let tree;
        let content = fs.readFileSync(filename, {encoding: 'utf-8'});
        // let message = `process ${filename} file, level: ${level}, vertexes: ${vertexes.size}, edges: ${edges.size}`;
        const contentDigest = sha1(content);
        const cacheFile = cacheDir + '/' + contentDigest;

        function pad(str, len) {
            let pad = '';
            for(let i = 0; i < len; i++) {
                pad += ' ';
            }
            return pad + str;
        }

        vertexes.add(filename);

        function traverse(node) {
            function addFiles(className, property) {
                let prefix = '';
                if(property && configMap[property].prefix) {
                    prefix = configMap[property].prefix;
                }
                for(let file of getRequireFile(className, prefix)) {
                    let edge = `${filename}, ${file}`;
                    children.push({name: file, children: []});
                    if(property === 'uses') {
                        edge = `${file}, ${filename}`;
                    }
                    if(!edges.has(edge)) {
                        edges.add(edge);
                    } else {
                        if(debug) console.log('skip edge!')
                    }
                }
            }

            if(node && node.comments) {
                for(let comment of node.comments) {
                    if(comment.type === 'Line' && comment.value.includes('@require')) {
                        addFiles(comment.value.replace('@require ', '').trim(), null);
                    }
                }
            }
            if(node && node.type === 'Property' && node.key && properties.includes(node.key.name)) {
                const nodeName = node.key.name;

                function isType(node, name) {
                    return node && node.value && node.value.type === name;
                }

                if(isType(node, 'Literal')) {
                    if(node.value.value !== null) {
                        addFiles(node.value.value, nodeName);
                    }
                } else if(isType(node, 'ArrayExpression')) {
                    node.value.elements.forEach(function(element) {
                        addFiles(element.value, nodeName);
                    })
                } else if(isType(node, 'ObjectExpression') && node.value.properties && node.value.properties.length > 0 && configMap[node.key.name].allowObject) {
                    node.value.properties.forEach(function(objectNode) {
                        if(isType(objectNode, 'Literal')) {
                            addFiles(objectNode.value.value, nodeName);
                        }
                    })
                }
            }
        }

        /**
         * Process each possible ways how required files can be referenced in Ext.js
         * The regexp's below are dealing with the following cases:
         * - requires: [...]
         * - controllers: [...]
         * - stores: [...]
         * - controller: '...' (ViewController definition in the View class)
         * - sViewCache - specific to our codebase - sorry :-)
         *
         * In case of stores and controllers the full namespace is automatically added
         * to the require if not full reference is found
         */
        // провераяем разбирали этот файл ранее если да, то берем результат из cache
        if(fs.existsSync(cacheFile)) {
            tree = JSON.parse(fs.readFileSync(cacheFile).toString());
        } else {
            try {
                tree = esprima.parseScript(content, {
                    range: true,
                    comment: true
                });
                fs.writeFileSync(cacheFile, JSON.stringify(tree));
            } catch(error) {
                console.error(filename, chalk.red('error parsing: ') + error);
                process.exit(1);
            }
        }

        esUtils.parentize(tree);
        esUtils.traverse(tree, traverse);
        if(debug) console.log(pad(`${filename}`, level), children.map(item => {
            let last = item.name.lastIndexOf('/') + 1;
            return item.name.substr(last);
        }).join(', '));
        if(children.length) {
            for(let item of children) {
                if(!vertexes.has(item.name)) {
                    makeGraph(item, level + 1, vertexes, edges);
                }
            }
        }
    }

    try {
        let edges = new Set();
        let vertexes = new Set();

        makeGraph(root, 0, vertexes, edges);

        let filtered = [];
        for(let edge of edges.entries()) {
            let item = edge[0].split(', ');
            if(item[0] !== item[1]) {
                filtered.push(item);
            }
        }
        if(debug) {
            let loops = hasLoop(Array.from(vertexes), filtered);
            console.log(loops);
        }
        let k = topologySort(Array.from(vertexes), filtered);
        return {global: root, order: k};
        // return {global: root, order: toposort(filtered).reverse()};

    } catch(error) {
        console.error(chalk.red('error parsing: ') + error);
    }

};

//
// Detect loop in a directed graph, use graph coloring algorithm.
//
// @param vertices - array of vertices, a vertex is either an integer or a
//                   string
// @param edges - array of edges, an edge is an array of length 2 which
//                marks the source and destination vertice.
//                i.e., [source, dest]
//
// @return { hasLoop: true, loop: [...] }
//
function hasLoop(vertices, edges) {
    const WHITE = 0;
    const GRAY = 1;
    const BLACK = 2;
    let colors = {};
    let path = [];

    function _hasLoopDFS(vertices, edges, colors, path, vertex) {
        colors[vertex] = GRAY;
        path.push(vertex);

        let adjacentEdges = [];
        for(let i = 0; i < edges.length; ++i) {
            let edge = edges[i];
            if(edge[0] === vertex) {
                adjacentEdges.push(edge)
            }
        }

        for(let i = 0; i < adjacentEdges.length; ++i) {
            let edge = adjacentEdges[i];
            let adjVertex = edge[1];

            if(colors[adjVertex] === GRAY) {
                let loop = path.slice(path.indexOf(adjVertex));
                return {hasLoop: true, loop: loop}
            }

            if(colors[adjVertex] === WHITE) {
                let result = _hasLoopDFS(vertices, edges, colors, path, adjVertex);
                if(result.hasLoop) {
                    return result
                }
            }
        }

        colors[vertex] = BLACK;
        path.pop(vertex);

        return {hasLoop: false}
    }

    // Initialize colors to white
    for(let i = 0; i < vertices.length; ++i) {
        colors[vertices[i]] = WHITE
    }

    // For all vertices, do DFS traversal
    for(let i = 0; i < vertices.length; ++i) {
        let vertex = vertices[i];
        if(colors[vertex] === WHITE) {
            let result = _hasLoopDFS(vertices, edges, colors, path, vertex);

            if(result.hasLoop) {
                return result
            }
        }
    }

    return {hasLoop: false}
}

function topologySort(vertexes, edges) {
    let init = [];
    let sorted = [];

    function adjacencyMatrix(vertexes, edges) {
        let matrix = [];
        for(let y of vertexes) {
            let row = [];
            for(let x of vertexes) {
                let value = 0;
                for(let edge of edges) {
                    if(edge[0].indexOf(y) !== -1 && edge[1].indexOf(x) !== -1) {
                        value += 1;
                    }
                }
                row.push(value);
            }
            matrix.push(row);
        }
        return matrix;
    }

    function sumByColumn(matrix, exclude) {
        let B = [];
        for(let i = 0; i < vertexes.length; i++) {
            B.push(null);
        }
        for(let i = 0; i < vertexes.length; i++) {
            if(!exclude.includes(i)) {
                for(let j = 0; j < vertexes.length; j++) {
                    if(!exclude.includes(j)) {
                        B[i] += matrix[i][j];
                    }
                }
            }
        }
        return B;
    }

    function process(B, exclude, func) {
        for(let i = 0; i < B.length; i++) {
            if(B[i] === -1 || B[i] === 0 && !exclude.includes(i)) {
                func(vertexes[i]);
            }
        }
    }

    let matrix = adjacencyMatrix(vertexes, edges);

    while(true) {
        let B = sumByColumn(matrix, init);
        process(B, init, el => sorted.push(el));
        init.length = 0;
        for(let i = 0; i < B.length; i++) {
            if(B[i] === 0 || B[i] === null) {
                init.push(i);
            }
        }
        if(!B.filter(element => element === 0).length) {
            break;
        }
    }
    return sorted;
}

module.exports = {parse, sha1};
