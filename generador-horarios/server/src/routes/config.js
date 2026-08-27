import { Router } from "express";
import { readDB, writeDB } from "../store/db.js";

const router = Router();

router.get("/", (req, res) => {
  const db = readDB();
  res.json(db.config);
});

router.put("/", (req, res) => {
  const db = readDB();
  db.config = { ...db.config, ...req.body };
  writeDB(db);
  res.json(db.config);
});

export default router;
