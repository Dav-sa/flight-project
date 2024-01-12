"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const URL = require("url");
const MongoDb = require("mongodb");
const Factory_1 = require("../lib/Factory");
const Server_1 = require("./Server");
const Utils_1 = require("./Utils");
class MongoManager {
    constructor() {
        this._servers = {};
    }
    async connect(host) {
        const urlStr = host.path.startsWith('mongodb')
            ? host.path
            : `mongodb://${host.path}`;
        const url = URL.parse(urlStr);
        let hostname = url.host || host.path;
        if (this._servers[hostname] instanceof Server_1.Server) {
            // Already connected
            return;
        }
        try {
            const client = await MongoDb.MongoClient.connect(urlStr, {
                useNewUrlParser: true
            });
            const server = new Server_1.Server(hostname, client);
            this._servers[hostname] = server;
            console.info(`[${hostname}] Connected to ${hostname}`);
            await this.checkAuth(hostname);
        }
        catch (err) {
            console.error(`Error while connecting to ${hostname}:`, err.code, err.message);
            this._servers[hostname] = err;
        }
    }
    getServer(name) {
        const server = this._servers[name] || this._servers[`${name}:27017`];
        if (!server) {
            throw new Error('Server does not exist');
        }
        return server;
    }
    async checkAuth(name) {
        const server = this.getServer(name);
        if (server instanceof Error) {
            return;
        }
        try {
            await server.toJson();
        }
        catch (err) {
            console.log(require('util').inspect(err, false, 20));
            if (err.code == 13 && err.codeName == "Unauthorized") {
                this._servers[name] = err;
            }
        }
    }
    async load() {
        let hosts = await Factory_1.default.hostsManager.getHosts();
        await Promise.all(hosts.map((h) => this.connect(h)));
    }
    removeServer(name) {
        delete this._servers[name];
    }
    async getServersJson() {
        const servers = [];
        for (const [name, server] of Object.entries(this._servers)) {
            if (server instanceof Error) {
                servers.push({
                    name: name,
                    error: {
                        code: server.code,
                        name: server.name,
                        message: server.message
                    }
                });
            }
            else {
                const json = await server.toJson();
                servers.push(json);
            }
        }
        Utils_1.Utils.fieldSort(servers, "name");
        return servers;
    }
    async getDatabasesJson(serverName) {
        const server = this.getServer(serverName);
        if (server instanceof Error) {
            return [];
        }
        const json = await server.toJson();
        return json.databases;
    }
    async getCollectionsJson(serverName, databaseName) {
        const server = this.getServer(serverName);
        if (server instanceof Error) {
            return [];
        }
        const database = await server.database(databaseName);
        if (!database) {
            return [];
        }
        const json = await database.toJson();
        return json.collections;
    }
    async getCollection(serverName, databaseName, collectionName) {
        const server = this.getServer(serverName);
        if (server instanceof Error) {
            return;
        }
        const database = await server.database(databaseName);
        if (!database) {
            return;
        }
        const collection = await database.collection(collectionName);
        return collection;
    }
}
exports.MongoManager = MongoManager;
