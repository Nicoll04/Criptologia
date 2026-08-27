// Grid de selección de disponibilidad (día x bloque). Si `value` está vacío,
// se interpreta como "disponible en todos los horarios".
export default function AvailabilityGrid({ config, value, onChange }) {
  const selected = new Set((value || []).map((s) => `${s.dia}|${s.bloqueId}`));

  function toggle(dia, bloqueId) {
    const key = `${dia}|${bloqueId}`;
    // Si estaba en modo "todo disponible" (lista vacía), materializamos el set
    // completo primero para poder apagar solo la celda clickeada.
    let base = selected;
    if ((value || []).length === 0) {
      base = new Set();
      for (const d of config.dias) {
        for (const b of config.bloques) base.add(`${d}|${b.id}`);
      }
    }
    const next = new Set(base);
    if (next.has(key)) next.delete(key);
    else next.add(key);
    const list = Array.from(next).map((k) => {
      const [d, b] = k.split("|");
      return { dia: d, bloqueId: b };
    });
    onChange(list);
  }

  function selectAll() {
    onChange([]);
  }

  return (
    <div className="availability-grid">
      <div className="availability-header">
        <span>Disponibilidad semanal</span>
        <button type="button" className="link" onClick={selectAll}>
          Marcar todo disponible
        </button>
      </div>
      <table className="grid-table">
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
                const key = `${dia}|${bloque.id}`;
                const isFullyOpen = (value || []).length === 0;
                const active = isFullyOpen || selected.has(key);
                return (
                  <td key={key}>
                    <button
                      type="button"
                      className={`cell-toggle ${active ? "on" : ""}`}
                      onClick={() => toggle(dia, bloque.id)}
                      aria-label={`${dia} ${bloque.etiqueta}`}
                    />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
