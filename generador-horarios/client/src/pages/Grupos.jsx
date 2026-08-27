import { useState } from "react";
import { api } from "../api";
import { useData } from "../context/DataContext";

const emptyForm = { nombre: "", asignaturas: [] };
const emptyRow = { subjectId: "", teacherId: "", horasSemana: 1 };

export default function Grupos() {
  const { groups, subjects, teachers, reload } = useData();
  const [form, setForm] = useState(emptyForm);
  const [row, setRow] = useState(emptyRow);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(null);

  const teachersForSubject = (subjectId) =>
    teachers.filter((t) => (t.materias || []).includes(subjectId));

  function addRow() {
    if (!row.subjectId || !row.teacherId || Number(row.horasSemana) <= 0) return;
    if (form.asignaturas.some((a) => a.subjectId === row.subjectId)) {
      setError("Esa materia ya está agregada a este grupo.");
      return;
    }
    setError(null);
    setForm((f) => ({
      ...f,
      asignaturas: [...f.asignaturas, { ...row, horasSemana: Number(row.horasSemana) }],
    }));
    setRow(emptyRow);
  }

  function removeRow(subjectId) {
    setForm((f) => ({ ...f, asignaturas: f.asignaturas.filter((a) => a.subjectId !== subjectId) }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.nombre.trim()) return;
    setError(null);
    const payload = { ...form, nombre: form.nombre.trim() };
    try {
      if (editingId) {
        await api.updateGroup(editingId, payload);
      } else {
        await api.createGroup(payload);
      }
      setForm(emptyForm);
      setEditingId(null);
      await reload();
    } catch (err) {
      setError(err.message);
    }
  }

  function startEdit(g) {
    setEditingId(g.id);
    setForm({ nombre: g.nombre, asignaturas: g.asignaturas || [] });
  }

  async function handleDelete(id) {
    if (!confirm("¿Eliminar este grupo?")) return;
    await api.deleteGroup(id);
    await reload();
  }

  function subjectName(id) {
    return subjects.find((s) => s.id === id)?.nombre || "?";
  }
  function teacherName(id) {
    return teachers.find((t) => t.id === id)?.nombre || "?";
  }

  const totalHoras = form.asignaturas.reduce((sum, a) => sum + Number(a.horasSemana || 0), 0);

  return (
    <div className="page">
      <h1>Grupos / Cursos</h1>

      <form className="stacked-form" onSubmit={handleSubmit}>
        <label>
          Nombre del grupo
          <input
            type="text"
            value={form.nombre}
            onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
            placeholder="Ej. 10-A"
          />
        </label>

        <fieldset>
          <legend>Carga académica (materias y horas semanales)</legend>

          {subjects.length === 0 || teachers.length === 0 ? (
            <p className="hint">Registra materias y profesores antes de armar la carga académica.</p>
          ) : (
            <div className="row-builder">
              <select
                value={row.subjectId}
                onChange={(e) => setRow((r) => ({ ...r, subjectId: e.target.value, teacherId: "" }))}
              >
                <option value="">Materia...</option>
                {subjects.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.nombre}
                  </option>
                ))}
              </select>

              <select
                value={row.teacherId}
                onChange={(e) => setRow((r) => ({ ...r, teacherId: e.target.value }))}
                disabled={!row.subjectId}
              >
                <option value="">Profesor...</option>
                {teachersForSubject(row.subjectId).map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.nombre}
                  </option>
                ))}
              </select>

              <input
                type="number"
                min="1"
                max="40"
                value={row.horasSemana}
                onChange={(e) => setRow((r) => ({ ...r, horasSemana: e.target.value }))}
                title="Horas semanales"
              />

              <button type="button" onClick={addRow}>
                Agregar
              </button>
            </div>
          )}
          {row.subjectId && teachersForSubject(row.subjectId).length === 0 && (
            <p className="hint">Ningún profesor tiene esta materia asignada todavía.</p>
          )}

          <table className="data-table small">
            <thead>
              <tr>
                <th>Materia</th>
                <th>Profesor</th>
                <th>Horas/semana</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {form.asignaturas.map((a) => (
                <tr key={a.subjectId}>
                  <td>{subjectName(a.subjectId)}</td>
                  <td>{teacherName(a.teacherId)}</td>
                  <td>{a.horasSemana}</td>
                  <td className="actions">
                    <button type="button" className="link danger" onClick={() => removeRow(a.subjectId)}>
                      Quitar
                    </button>
                  </td>
                </tr>
              ))}
              {form.asignaturas.length === 0 && (
                <tr>
                  <td colSpan={4} className="empty">
                    Sin materias agregadas.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
          {form.asignaturas.length > 0 && <p className="hint">Total: {totalHoras}h/semana</p>}
        </fieldset>

        <div className="form-actions">
          <button type="submit">{editingId ? "Guardar cambios" : "Agregar grupo"}</button>
          {editingId && (
            <button
              type="button"
              className="secondary"
              onClick={() => {
                setEditingId(null);
                setForm(emptyForm);
              }}
            >
              Cancelar
            </button>
          )}
        </div>
      </form>
      {error && <p className="error">{error}</p>}

      <table className="data-table">
        <thead>
          <tr>
            <th>Grupo</th>
            <th>Materias</th>
            <th>Horas/semana</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {groups.map((g) => (
            <tr key={g.id}>
              <td>{g.nombre}</td>
              <td>{(g.asignaturas || []).length}</td>
              <td>{(g.asignaturas || []).reduce((sum, a) => sum + Number(a.horasSemana || 0), 0)}</td>
              <td className="actions">
                <button className="link" onClick={() => startEdit(g)}>
                  Editar
                </button>
                <button className="link danger" onClick={() => handleDelete(g.id)}>
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
          {groups.length === 0 && (
            <tr>
              <td colSpan={4} className="empty">
                Todavía no hay grupos registrados.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
