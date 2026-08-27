import { Router } from "express";
import { v4 as uuid } from "uuid";
import { readDB, writeDB } from "../store/db.js";

// Generic CRUD router factory for a top-level collection in db.json
export function crudRouter(collectionName, { onWrite } = {}) {
  const router = Router();

  router.get("/", (req, res) => {
    const db = readDB();
    res.json(db[collectionName] || []);
  });

  router.post("/", (req, res) => {
    const db = readDB();
    const item = { id: uuid(), ...req.body };
    db[collectionName] = db[collectionName] || [];
    db[collectionName].push(item);
    if (onWrite) onWrite(db);
    writeDB(db);
    res.status(201).json(item);
  });

  router.put("/:id", (req, res) => {
    const db = readDB();
    const list = db[collectionName] || [];
    const idx = list.findIndex((it) => it.id === req.params.id);
    if (idx === -1) return res.status(404).json({ error: "No encontrado" });
    list[idx] = { ...list[idx], ...req.body, id: req.params.id };
    if (onWrite) onWrite(db);
    writeDB(db);
    res.json(list[idx]);
  });

  router.delete("/:id", (req, res) => {
    const db = readDB();
    const list = db[collectionName] || [];
    const idx = list.findIndex((it) => it.id === req.params.id);
    if (idx === -1) return res.status(404).json({ error: "No encontrado" });
    const [removed] = list.splice(idx, 1);
    if (onWrite) onWrite(db);
    writeDB(db);
    res.json(removed);
  });

  return router;
}
