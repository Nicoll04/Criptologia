import { Router } from "express";
import { readDB, writeDB } from "../store/db.js";
import { generateSchedule } from "../scheduler/solver.js";

const router = Router();

router.get("/", (req, res) => {
  const db = readDB();
  res.json(db.lastSchedule || null);
});

router.post("/generate", (req, res) => {
  const db = readDB();
  const result = generateSchedule(db);
  db.lastSchedule = result;
  writeDB(db);
  res.json(result);
});

export default router;
