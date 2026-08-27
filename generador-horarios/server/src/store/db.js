import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DB_FILE = path.join(__dirname, "..", "..", "data", "db.json");

const DEFAULT_DATA = {
  config: {
    dias: ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"],
    bloques: [
      { id: "b1", etiqueta: "07:00 - 07:50" },
      { id: "b2", etiqueta: "07:50 - 08:40" },
      { id: "b3", etiqueta: "08:40 - 09:30" },
      { id: "b4", etiqueta: "09:50 - 10:40" },
      { id: "b5", etiqueta: "10:40 - 11:30" },
      { id: "b6", etiqueta: "11:30 - 12:20" },
    ],
  },
  subjects: [],
  teachers: [],
  groups: [],
  lastSchedule: null,
};

function ensureFile() {
  const dir = path.dirname(DB_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  if (!fs.existsSync(DB_FILE)) {
    fs.writeFileSync(DB_FILE, JSON.stringify(DEFAULT_DATA, null, 2));
  }
}

export function readDB() {
  ensureFile();
  const raw = fs.readFileSync(DB_FILE, "utf-8");
  try {
    return JSON.parse(raw);
  } catch {
    return structuredClone(DEFAULT_DATA);
  }
}

export function writeDB(data) {
  ensureFile();
  fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));
}
