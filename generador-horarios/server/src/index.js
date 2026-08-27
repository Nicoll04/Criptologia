import express from "express";
import cors from "cors";
import { crudRouter } from "./routes/crud.js";
import configRouter from "./routes/config.js";
import scheduleRouter from "./routes/schedule.js";

const app = express();
app.use(cors());
app.use(express.json());

app.use("/api/subjects", crudRouter("subjects"));
app.use("/api/teachers", crudRouter("teachers"));
app.use("/api/groups", crudRouter("groups"));
app.use("/api/config", configRouter);
app.use("/api/schedule", scheduleRouter);

app.get("/api/health", (req, res) => res.json({ ok: true }));

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`Servidor de horarios escuchando en http://localhost:${PORT}`);
});
