"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const MongoDb = require("mongodb");
const JsonEncoder_1 = require("../lib/JsonEncoder");
class Collection {
    constructor(collection) {
        this.countTimeout = parseInt(process.env.MONGOKU_COUNT_TIMEOUT, 10) || 5000;
        this._collection = collection;
    }
    get name() {
        return this._collection.collectionName;
    }
    async findOne(document) {
        const obj = await this._collection.findOne({
            _id: new MongoDb.ObjectId(document)
        });
        return JsonEncoder_1.default.encode(obj);
    }
    find(query, project, sort, limit, skip) {
        return this._collection.find(JsonEncoder_1.default.decode(query))
            .project(project)
            .sort(JsonEncoder_1.default.decode(sort))
            .limit(limit)
            .skip(skip)
            .map((obj) => {
            return JsonEncoder_1.default.encode(obj);
        })
            .toArray();
    }
    async updateOne(document, newObj, partial) {
        const newValue = JsonEncoder_1.default.decode(newObj);
        const update = partial ? { '$set': newValue } : JsonEncoder_1.default.decode(newValue);
        await this._collection.replaceOne({
            _id: new MongoDb.ObjectId(document)
        }, update);
        return JsonEncoder_1.default.encode(newValue);
    }
    async removeOne(document) {
        await this._collection.deleteOne({
            _id: new MongoDb.ObjectId(document)
        });
    }
    count(query) {
        if (query && Object.keys(query).length > 0) {
            return this._collection.countDocuments(JsonEncoder_1.default.decode(query), {
                maxTimeMS: this.countTimeout
            }).catch(_ => this._collection.estimatedDocumentCount());
        }
        // fast count
        return this._collection.estimatedDocumentCount();
    }
    async toJson() {
        let stats = {
            size: 0,
            count: 0,
            avgObjSize: 0,
            storageSize: 0,
            capped: false,
            nindexes: 0,
            totalIndexSize: 0,
            indexSizes: {}
        };
        try {
            stats = await this._collection.stats();
        }
        catch (err) { }
        ;
        return {
            name: this.name,
            size: (stats.storageSize || 0) + (stats.totalIndexSize || 0),
            dataSize: stats.size,
            count: stats.count,
            avgObjSize: stats.avgObjSize || 0,
            storageSize: stats.storageSize || 0,
            capped: stats.capped,
            nIndexes: stats.nindexes,
            totalIndexSize: stats.totalIndexSize || 0,
            indexSizes: stats.indexSizes
        };
    }
}
exports.Collection = Collection;
