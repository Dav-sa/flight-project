"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express = require("express");
const bodyParser = require("body-parser");
const Factory_1 = require("../lib/Factory");
exports.api = express.Router();
// Get servers
exports.api.get('/servers', async (req, res, next) => {
    const servers = await Factory_1.default.mongoManager.getServersJson();
    return res.json(servers);
});
exports.api.put('/servers', bodyParser.json(), async (req, res, next) => {
    try {
        await Factory_1.default.hostsManager.add(req.body.url);
        await Factory_1.default.mongoManager.load();
    }
    catch (err) {
        return next(err);
    }
    return res.json({
        ok: true
    });
});
exports.api.delete('/servers/:server', async (req, res, next) => {
    try {
        await Factory_1.default.hostsManager.remove(req.params.server);
        Factory_1.default.mongoManager.removeServer(req.params.server);
    }
    catch (err) {
        return next(err);
    }
    return res.json({
        ok: true
    });
});
exports.api.get('/servers/:server/databases', async (req, res, next) => {
    const server = req.params.server;
    try {
        const databases = await Factory_1.default.mongoManager.getDatabasesJson(server);
        return res.json(databases);
    }
    catch (err) {
        return next(err);
    }
});
exports.api.get('/servers/:server/databases/:database/collections', async (req, res, next) => {
    const server = req.params.server;
    const database = req.params.database;
    try {
        const collections = await Factory_1.default.mongoManager.getCollectionsJson(server, database);
        return res.json(collections);
    }
    catch (err) {
        return next(err);
    }
});
exports.api.get('/servers/:server/databases/:database/collections/:collection/documents/:document', async (req, res, next) => {
    const server = req.params.server;
    const database = req.params.database;
    const collection = req.params.collection;
    const document = req.params.document;
    try {
        const c = await Factory_1.default.mongoManager.getCollection(server, database, collection);
        if (!c) {
            return next(new Error(`Collection not found: ${server}.${database}.${collection}`));
        }
        const doc = await c.findOne(document);
        if (!doc) {
            return next(new Error("This document does not exist"));
        }
        return res.json({
            ok: true,
            document: doc
        });
    }
    catch (err) {
        return next(err);
    }
});
exports.api.post('/servers/:server/databases/:database/collections/:collection/documents/:document', bodyParser.json(), async (req, res, next) => {
    const server = req.params.server;
    const database = req.params.database;
    const collection = req.params.collection;
    const document = req.params.document;
    const partial = !!req.query.partial;
    try {
        const c = await Factory_1.default.mongoManager.getCollection(server, database, collection);
        if (!c) {
            return next(new Error(`Collection not found: ${server}.${database}.${collection}`));
        }
        const update = await c.updateOne(document, req.body, partial);
        return res.json({
            ok: true,
            update: update
        });
    }
    catch (err) {
        return next(err);
    }
});
exports.api.delete('/servers/:server/databases/:database/collections/:collection/documents/:document', async (req, res, next) => {
    const server = req.params.server;
    const database = req.params.database;
    const collection = req.params.collection;
    const document = req.params.document;
    try {
        const c = await Factory_1.default.mongoManager.getCollection(server, database, collection);
        if (!c) {
            return next(new Error(`Collection not found: ${server}.${database}.${collection}`));
        }
        await c.removeOne(document);
        return res.json({
            ok: true
        });
    }
    catch (err) {
        return next(err);
    }
});
exports.api.get('/servers/:server/databases/:database/collections/:collection/query', async (req, res, next) => {
    const server = req.params.server;
    const database = req.params.database;
    const collection = req.params.collection;
    let query = req.query.q;
    if (typeof query !== "object") {
        try {
            query = JSON.parse(query);
        }
        catch (err) {
            return next(new Error(`Invalid query: ${query}`));
        }
    }
    let sort = req.query.sort || "{}";
    if (sort && typeof sort !== "object") {
        try {
            sort = JSON.parse(sort);
        }
        catch (err) {
            return next(new Error(`Invalid order: ${sort}`));
        }
    }
    let project = req.query.project || "";
    if (project && typeof project !== "object") {
        try {
            project = JSON.parse(project);
        }
        catch (err) {
            return next(new Error(`Invalid project: ${project}`));
        }
    }
    let limit = parseInt(req.query.limit, 10);
    if (isNaN(limit)) {
        limit = 20;
    }
    let skip = parseInt(req.query.skip, 10);
    if (isNaN(skip)) {
        skip = 0;
    }
    const c = await Factory_1.default.mongoManager.getCollection(server, database, collection);
    if (!c) {
        return next(new Error(`Collection not found: ${server}.${database}.${collection}`));
    }
    try {
        const results = await c.find(query, project, sort, limit, skip);
        return res.json({
            ok: true,
            results: results
        });
    }
    catch (err) {
        return next(err);
    }
});
exports.api.get('/servers/:server/databases/:database/collections/:collection/count', async (req, res, next) => {
    const server = req.params.server;
    const database = req.params.database;
    const collection = req.params.collection;
    let query = req.query.q;
    if (typeof query !== "object") {
        try {
            query = JSON.parse(query);
        }
        catch (err) {
            return next(new Error(`Invalid query: ${query}`));
        }
    }
    const c = await Factory_1.default.mongoManager.getCollection(server, database, collection);
    if (!c) {
        return next(new Error(`Collection not found: ${server}.${database}.${collection}`));
    }
    try {
        const count = await c.count(query);
        return res.json({
            ok: true,
            count: count
        });
    }
    catch (err) {
        return next(err);
    }
});
