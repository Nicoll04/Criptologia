import { useState } from "react";
import { api } from "../api";
import { useData } from "../context/DataContext";
import AvailabilityGrid from "../components/AvailabilityGrid";

const emptyForm = {
  nombre: "",
  materias: [],
  horasPedagogicasSemana: 0,
  disponibilidad: [],
};

export default function Profesores() {
  const { teachers, subjects, config, groups, reload } = useData();
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(null);

  function toggleMateria(id) {
    setForm((f) => ({
      ...f,
      materias: f.materias.includes(id)
        ? f.materias.filter((m) => m !== id)
        : [...f.materias, id],
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.nombre.trim()) return;
    setError(null);
    const payload = {
      ...form,
      nombre: form.nombre.trim(),
      horasPedagogicasSemana: Number(form.horasPedagogicasSemana) || 0,
    };
    try {
      if (editingId) {
        await api.updateTeacher(editingId, payload);
      } else {
        await api.createTeacher(payload);
      }
      setForm(emptyForm);
      setEditingId(null);
      await reload();
    } catch (err) {
      setError(err.message);
    }
  }

  function startEdit(t) {
    setEditingId(t.id);
    setForm({
      nombre: t.nombre,
      materias: t.materias || [],
      horasPedagogicasSemana: t.horasPedagogicasSemana || 0,
      disponibilidad: t.disponibilidad || [],
    });
  }

  function teacherInUse(id) {
    return groups.some((g) => (g.asignaturas || []).some((a) => a.teacherId === id));
  }

  async function handleDelete(id) {
    if (teacherInUse(id)) {
      setError("No se puede eliminar: hay grupos con clases asignadas a este profesor.");
      return;
    }
    if (!confirm("¿Eliminar este profesor?")) return;
    await api.deleteTeacher(id);
    await reload();
  }

  function subjectName(id) {
    return subjects.find((s) => s.id === id)?.nombre || "?";
  }

  return (
    <div className="page">
      <h1>Profesores</h1>

      <form className="stacked-form" onSubmit={handleSubmit}>
        <label>
          Nombre
          <input
            type="text"
            value={form.nombre}
            onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
            placeholder="Nombre del profesor"
          />
        </label>

        <fieldset>
          <legend>Materias que dicta</legend>
          {subjects.length === 0 && <p className="hint">Primero registra materias.</p>}
          <div className="checkbox-list">
            {subjects.map((s) => (
              <label key={s.id} className="checkbox">
                <input
                  type="checkbox"
                  checked={form.materias.includes(s.id)}
                  onChange={() => toggleMateria(s.id)}
                />
                {s.nombre}
              </label>
            ))}
          </div>
        </fieldset>

        <label className="short">
          Horas de tiempo pedagógico por semana
          <input
            type="number"
            min="0"
            value={form.horasPedagogicasSemana}
            onChange={(e) => setForm((f) => ({ ...f, horasPedagogicasSemana: e.target.value }))}
          />
        </label>
        <p className="hint">
          Bloques que deben quedar libres (planeación, calificación) y no se usarán para dictar clase.
        </p>

        {config.dias.length > 0 && (
          <AvailabilityGrid
            config={config}
            value={form.disponibilidad}
            onChange={(list) => setForm((f) => ({ ...f, disponibilidad: list }))}
          />
        )}

        <div className="form-actions">
          <button type="submit">{editingId ? "Guardar cambios" : "Agregar profesor"}</button>
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
            <th>Profesor</th>
            <th>Materias</th>
            <th>Tiempo pedagógico</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {teachers.map((t) => (
            <tr key={t.id}>
              <td>{t.nombre}</td>
              <td>{(t.materias || []).map(subjectName).join(", ") || "—"}</td>
              <td>{t.horasPedagogicasSemana || 0}h/semana</td>
              <td className="actions">
                <button className="link" onClick={() => startEdit(t)}>
                  Editar
                </button>
                <button className="link danger" onClick={() => handleDelete(t.id)}>
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
          {teachers.length === 0 && (
            <tr>
              <td colSpan={4} className="empty">
                Todavía no hay profesores registrados.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
