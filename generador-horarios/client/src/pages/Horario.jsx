import { useEffect, useState } from "react";
import { api } from "../api";
import { useData } from "../context/DataContext";

export default function Horario() {
  const { config, groups, teachers } = useData();
  const [schedule, setSchedule] = useState(null);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState("grupo"); // "grupo" | "profesor"
  const [selectedId, setSelectedId] = useState("");

  useEffect(() => {
    api.getSchedule().then(setSchedule).catch(() => {});
  }, []);

  useEffect(() => {
    const list = view === "grupo" ? groups : teachers;
    if (list.length > 0 && !list.some((x) => x.id === selectedId)) {
      setSelectedId(list[0].id);
    }
  }, [view, groups, teachers, selectedId]);

  async function handleGenerate() {
    setLoading(true);
    try {
      const result = await api.generateSchedule();
      setSchedule(result);
    } finally {
      setLoading(false);
    }
  }

  function lessonsFor(id) {
    if (!schedule || !schedule.success) return [];
    return schedule.lessons.filter((l) => (view === "grupo" ? l.groupId === id : l.teacherId === id));
  }

  const lessons = lessonsFor(selectedId);
  const byCell = {};
  for (const l of lessons) byCell[`${l.dia}|${l.bloqueId}`] = l;

  return (
    <div className="page">
      <h1>Horario</h1>

      <div className="form-actions">
        <button type="button" onClick={handleGenerate} disabled={loading}>
          {loading ? "Generando..." : "Generar horario"}
        </button>
      </div>

      {schedule && !schedule.success && (
        <div className="error-box">
          <p>{schedule.error}</p>
        </div>
      )}

      {schedule?.warnings?.length > 0 && (
        <div className="warning-box">
          <strong>Advertencias:</strong>
          <ul>
            {schedule.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {schedule?.success && (
        <>
          <div className="view-switch">
            <div className="tabs">
              <button
                className={view === "grupo" ? "tab active" : "tab"}
                onClick={() => setView("grupo")}
              >
                Por grupo
              </button>
              <button
                className={view === "profesor" ? "tab active" : "tab"}
                onClick={() => setView("profesor")}
              >
                Por profesor
              </button>
            </div>
            <select value={selectedId} onChange={(e) => setSelectedId(e.target.value)}>
              {(view === "grupo" ? groups : teachers).map((x) => (
                <option key={x.id} value={x.id}>
                  {x.nombre}
                </option>
              ))}
            </select>
          </div>

          {config.dias.length === 0 || config.bloques.length === 0 ? (
            <p className="hint">Configura días y bloques primero.</p>
          ) : (
            <table className="timetable">
              <thead>
                <tr>
                  <th></th>
                  {config.dias.map((dia) => (
                    <th key={dia}>{dia}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {config.bloques.map((bloque) => (
                  <tr key={bloque.id}>
                    <td className="block-label">{bloque.etiqueta}</td>
                    {config.dias.map((dia) => {
                      const cell = byCell[`${dia}|${bloque.id}`];
                      return (
                        <td key={dia} className={cell ? "filled" : ""}>
                          {cell && (
                            <div className="cell-content">
                              <strong>{cell.subjectName}</strong>
                              <span>{view === "grupo" ? cell.teacherName : cell.groupName}</span>
                            </div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </>
      )}

      {!schedule && <p className="hint">Aún no se ha generado ningún horario.</p>}
    </div>
  );
}
