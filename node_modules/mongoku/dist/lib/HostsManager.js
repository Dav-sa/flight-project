"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const path = require("path");
const fs = require("fs");
const os = require("os");
const util = require("util");
const Nedb = require("nedb");
const DEFAULT_HOSTS = process.env.MONGOKU_DEFAULT_HOST ? process.env.MONGOKU_DEFAULT_HOST.split(';') : ['localhost:27017'];
const DATABASE_FILE = process.env.MONGOKU_DATABASE_FILE || path.join(os.homedir(), '.mongoku.db');
class HostsManager {
    promise(fn) {
        return util.promisify(fn.bind(this._db));
    }
    async load() {
        let first = false;
        try {
            await fs.promises.stat(DATABASE_FILE);
        }
        catch (err) {
            first = true;
        }
        this._db = new Nedb({
            filename: DATABASE_FILE
        });
        const load = this.promise(this._db.loadDatabase);
        await load();
        if (first) {
            await Promise.all(DEFAULT_HOSTS.map(async (hostname) => {
                const insert = this.promise(this._db.insert);
                return await insert({
                    path: hostname
                });
            }));
        }
    }
    getHosts() {
        return new Promise((resolve, reject) => {
            this._db.find({}, (err, hosts) => {
                if (err) {
                    return reject(err);
                }
                else {
                    return resolve(hosts);
                }
            });
        });
    }
    async add(path) {
        return new Promise((resolve, reject) => {
            this._db.update({
                path: path
            }, {
                $set: {
                    path: path
                }
            }, { upsert: true }, (err) => {
                if (err) {
                    return reject(err);
                }
                else {
                    return resolve();
                }
            });
        });
    }
    async remove(path) {
        return new Promise((resolve, reject) => {
            this._db.remove({
                path: new RegExp(`${path}`)
            }, (err) => {
                if (err) {
                    return reject(err);
                }
                else {
                    return resolve();
                }
            });
        });
    }
}
exports.HostsManager = HostsManager;
