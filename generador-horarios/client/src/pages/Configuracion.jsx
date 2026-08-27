import { useEffect, useState } from "react";
import { api } from "../api";
import { useData } from "../context/DataContext";

let blockCounter = 0;
function newBlockId() {
  blockCounter += 1;
  return `nb${Date.now()}${blockCounter}`;
}

export default function Configuracion() {
  const { config, reload } = useData();
  const [dias, setDias] = useState([]);
  const [bloques, setBloques] = useState([]);
  const [nuevoDia, setNuevoDia] = useState("");
  const [nuevaEtiqueta, setNuevaEtiqueta] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setDias(config.dias || []);
    setBloques(config.bloques || []);
  }, [config]);

  function addDia() {
    const v = nuevoDia.trim();
    if (!v || dias.includes(v)) return;
    setDias([...dias, v]);
    setNuevoDia("");
  }

  function removeDia(d) {
    setDias(dias.filter((x) => x !== d));
  }

  function addBloque() {
    const v = nuevaEtiqueta.trim();
    if (!v) return;
    setBloques([...bloques, { id: newBlockId(), etiqueta: v }]);
    setNuevaEtiqueta("");
  }

  function removeBloque(id) {
    setBloques(bloques.filter((b) => b.id !== id));
  }

  async function handleSave() {
    await api.updateConfig({ dias, bloques });
    await reload();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <div className="page">
      <h1>Configuración del horario</h1>
      <p className="hint">
        Define los días de clase y los bloques horarios disponibles. Al cambiarlos, revisa la
        disponibilidad de los profesores.
      </p>

      <div className="config-columns">
        <fieldset>
          <legend>Días</legend>
          <ul className="editable-list">
            {dias.map((d) => (
              <li key={d}>
                {d}
                <button type="button" className="link danger" onClick={() => removeDia(d)}>
                  Quitar
                </button>
              </li>
            ))}
          </ul>
          <div className="row-builder">
            <input
              type="text"
              placeholder="Ej. Sábado"
              value={nuevoDia}
              onChange={(e) => setNuevoDia(e.target.value)}
            />
            <button type="button" onClick={addDia}>
              Agregar día
            </button>
          </div>
        </fieldset>

        <fieldset>
          <legend>Bloques horarios</legend>
          <ul className="editable-list">
            {bloques.map((b) => (
              <li key={b.id}>
                {b.etiqueta}
                <button type="button" className="link danger" onClick={() => removeBloque(b.id)}>
                  Quitar
                </button>
              </li>
            ))}
          </ul>
          <div className="row-builder">
            <input
              type="text"
              placeholder="Ej. 12:20 - 13:10"
              value={nuevaEtiqueta}
              onChange={(e) => setNuevaEtiqueta(e.target.value)}
            />
            <button type="button" onClick={addBloque}>
              Agregar bloque
            </button>
          </div>
        </fieldset>
      </div>

      <div className="form-actions">
        <button type="button" onClick={handleSave}>
          Guardar configuración
        </button>
        {saved && <span className="hint">Guardado ✓</span>}
      </div>
    </div>
  );
}
