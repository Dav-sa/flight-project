"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const Collection_1 = require("./Collection");
const Utils_1 = require("./Utils");
class Database {
    constructor(name, size, empty, db) {
        this.name = name;
        this.size = size;
        this.empty = empty;
        this._db = db;
    }
    async collections() {
        const cs = await this._db.collections();
        const collections = [];
        for (const c of cs) {
            const collection = new Collection_1.Collection(c);
            collections.push(collection);
        }
        return collections;
    }
    collection(name) {
        const c = this._db.collection(name);
        return new Collection_1.Collection(c);
    }
    async toJson() {
        let totalObjSize = 0;
        let totalObjNr = 0;
        let storageSize = 0;
        let indexSize = 0;
        let dataSize = 0;
        const collections = await this.collections();
        const csJson = [];
        for (const collection of collections) {
            const json = await collection.toJson();
            totalObjSize += json.avgObjSize * json.count;
            totalObjNr += json.count;
            storageSize += json.storageSize;
            indexSize += json.totalIndexSize;
            dataSize += json.dataSize;
            csJson.push(json);
        }
        Utils_1.Utils.fieldSort(csJson, 'name');
        return {
            name: this.name,
            size: this.size,
            dataSize: dataSize,
            avgObjSize: totalObjSize / totalObjNr,
            storageSize: storageSize,
            totalIndexSize: indexSize,
            empty: this.empty,
            collections: csJson
        };
    }
}
exports.Database = Database;
