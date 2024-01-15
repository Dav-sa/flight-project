"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const MongoManager_1 = require("./MongoManager");
const HostsManager_1 = require("./HostsManager");
class Factory {
    get _initializedError() {
        return new Error("Factory.load() must be called first");
    }
    get mongoManager() {
        if (!this._mongoManager) {
            throw this._initializedError;
        }
        return this._mongoManager;
    }
    get hostsManager() {
        if (!this._hostsManager) {
            throw this._initializedError;
        }
        return this._hostsManager;
    }
    async load() {
        // Start by initializing the host manager (needed for mongo manager)
        this._hostsManager = new HostsManager_1.HostsManager();
        await this._hostsManager.load();
        // Then we can initialize the mongo manager
        this._mongoManager = new MongoManager_1.MongoManager();
        await this._mongoManager.load();
    }
}
const factory = new Factory();
exports.default = factory;
