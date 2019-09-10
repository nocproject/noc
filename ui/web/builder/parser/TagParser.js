/**
 *
 * Does not make too much sense, used to be way more complicated
 *
 */
'use strict';

class TagParser {
    /**
     *
     * @param tag Object
     */
    constructor(tag) {
        this._type = tag.type;
        this._tag = tag.tag;
        this._name = tag.name;
    }

    get name() {
        return this._name;
    }

    get type() {
        return this._type;
    }

    get tag() {
        return this._tag;
    }

}

module.exports = TagParser;
// export { TagParser };
