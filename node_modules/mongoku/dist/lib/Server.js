"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const Database_1 = require("./Database");
const Utils_1 = require("./Utils");
class Server {
    get name() { return this._name; }
    get size() { return this._size; }
    constructor(name, client) {
        this._name = name;
        this._client = client;
    }
    async databases() {
        const db = this._client.db("test");
        const results = await db.admin().listDatabases();
        this._size = results.totalSize;
        const databases = [];
        if (Array.isArray(results.databases)) {
            for (const d of results.databases) {
                const db = this._client.db(d.name);
                const database = new Database_1.Database(d.name, d.sizeOnDisk, d.empty, db);
                databases.push(database);
            }
        }
        return databases;
    }
    async database(name) {
        const databases = await this.databases();
        return databases.find(d => d.name === name);
    }
    async toJson() {
        const databases = await this.databases();
        const dbsJson = [];
        for (const database of databases) {
            const json = await database.toJson();
            dbsJson.push(json);
        }
        Utils_1.Utils.fieldSort(dbsJson, 'name');
        return {
            name: this.name,
            size: this.size,
            databases: dbsJson
        };
    }
}
exports.Server = Server;
