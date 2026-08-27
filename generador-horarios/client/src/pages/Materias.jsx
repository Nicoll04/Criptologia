import { useState } from "react";
import { api } from "../api";
import { useData } from "../context/DataContext";

export default function Materias() {
  const { subjects, reload, groups } = useData();
  const [nombre, setNombre] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!nombre.trim()) return;
    setError(null);
    try {
      if (editingId) {
        await api.updateSubject(editingId, { nombre: nombre.trim() });
      } else {
        await api.createSubject({ nombre: nombre.trim() });
      }
      setNombre("");
      setEditingId(null);
      await reload();
    } catch (err) {
      setError(err.message);
    }
  }

  function startEdit(subject) {
    setEditingId(subject.id);
    setNombre(subject.nombre);
  }

  function subjectInUse(id) {
    return groups.some((g) => (g.asignaturas || []).some((a) => a.subjectId === id));
  }

  async function handleDelete(id) {
    if (subjectInUse(id)) {
      setError("No se puede eliminar: hay grupos que usan esta materia.");
      return;
    }
    if (!confirm("¿Eliminar esta materia?")) return;
    await api.deleteSubject(id);
    await reload();
  }

  return (
    <div className="page">
      <h1>Materias</h1>
      <form className="inline-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Nombre de la materia (ej. Matemáticas)"
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
        />
        <button type="submit">{editingId ? "Guardar cambios" : "Agregar materia"}</button>
        {editingId && (
          <button
            type="button"
            className="secondary"
            onClick={() => {
              setEditingId(null);
              setNombre("");
            }}
          >
            Cancelar
          </button>
        )}
      </form>
      {error && <p className="error">{error}</p>}

      <table className="data-table">
        <thead>
          <tr>
            <th>Materia</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {subjects.map((s) => (
            <tr key={s.id}>
              <td>{s.nombre}</td>
              <td className="actions">
                <button className="link" onClick={() => startEdit(s)}>
                  Editar
                </button>
                <button className="link danger" onClick={() => handleDelete(s.id)}>
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
          {subjects.length === 0 && (
            <tr>
              <td colSpan={2} className="empty">
                Todavía no hay materias registradas.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
