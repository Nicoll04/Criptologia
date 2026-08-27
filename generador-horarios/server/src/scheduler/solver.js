// Motor de generación de horarios escolares.
// Modela el problema como un CSP: cada "lección" (una hora de una materia
// para un grupo, dictada por un profesor) debe ubicarse en un slot
// (día, bloque) sin chocar con otras lecciones del mismo grupo o profesor,
// respetando la disponibilidad del profesor y dejando libres sus horas
// de tiempo pedagógico.

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function shuffle(arr, rnd) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function slotKey(dia, bloqueId) {
  return `${dia}|${bloqueId}`;
}

export function generateSchedule(db) {
  const config = db.config || { dias: [], bloques: [] };
  const teachers = db.teachers || [];
  const subjects = db.subjects || [];
  const groups = db.groups || [];

  const days = config.dias || [];
  const blockIds = (config.bloques || []).map((b) => b.id);
  const allSlots = [];
  for (const dia of days) {
    for (const bloqueId of blockIds) allSlots.push({ dia, bloqueId });
  }

  const teacherById = Object.fromEntries(teachers.map((t) => [t.id, t]));
  const subjectById = Object.fromEntries(subjects.map((s) => [s.id, s]));
  const groupById = Object.fromEntries(groups.map((g) => [g.id, g]));

  const warnings = [];

  if (allSlots.length === 0) {
    return {
      success: false,
      error: "Configura al menos un día y un bloque horario antes de generar el horario.",
      warnings,
    };
  }

  // Disponibilidad de cada profesor: si no definió ninguna, se asume disponible en todos los slots.
  const teacherAvailSet = {};
  for (const t of teachers) {
    const avail = t.disponibilidad && t.disponibilidad.length > 0 ? t.disponibilidad : allSlots;
    teacherAvailSet[t.id] = new Set(avail.map((s) => slotKey(s.dia, s.bloqueId)));
  }

  // Validar carga académica vs. disponibilidad menos tiempo pedagógico.
  const teacherLoad = {};
  for (const t of teachers) teacherLoad[t.id] = 0;
  for (const g of groups) {
    for (const a of g.asignaturas || []) {
      if (!teacherById[a.teacherId]) continue;
      teacherLoad[a.teacherId] = (teacherLoad[a.teacherId] || 0) + Number(a.horasSemana || 0);
    }
  }
  // Tope real de horas de clase por profesor: su disponibilidad menos el
  // tiempo pedagógico que debe quedar libre. Es una restricción dura del
  // solver, no solo informativa.
  const teacherMaxLoad = {};
  let overloaded = false;
  for (const t of teachers) {
    const availCount = teacherAvailSet[t.id] ? teacherAvailSet[t.id].size : 0;
    const pedagogicas = Number(t.horasPedagogicasSemana || 0);
    const maxLoad = Math.max(0, availCount - pedagogicas);
    teacherMaxLoad[t.id] = maxLoad;
    const load = teacherLoad[t.id] || 0;
    if (load > maxLoad) {
      overloaded = true;
      warnings.push(
        `El profesor ${t.nombre} tiene ${load}h de clase asignadas, pero solo dispone de ${maxLoad}h ` +
          `(${availCount}h disponibles menos ${pedagogicas}h de tiempo pedagógico). Reduce su carga o amplía su disponibilidad.`
      );
    }
  }

  if (overloaded) {
    return {
      success: false,
      error:
        "No es posible generar el horario: la carga académica de uno o más profesores supera su disponibilidad una vez separado su tiempo pedagógico.",
      warnings,
    };
  }

  // Construir la lista de lecciones (una entrada por cada hora semanal).
  const lessons = [];
  let counter = 0;
  for (const g of groups) {
    for (const a of g.asignaturas || []) {
      const n = Number(a.horasSemana || 0);
      if (!teacherById[a.teacherId]) {
        warnings.push(`El grupo ${g.nombre} tiene una asignatura sin profesor válido asignado.`);
        continue;
      }
      for (let i = 0; i < n; i++) {
        lessons.push({
          uid: `L${counter++}`,
          groupId: g.id,
          subjectId: a.subjectId,
          teacherId: a.teacherId,
        });
      }
    }
  }

  if (lessons.length === 0) {
    return {
      success: false,
      error: "No hay horas de clase configuradas en ningún grupo todavía.",
      warnings,
    };
  }

  function computeDomain(lesson, state) {
    const availSet = teacherAvailSet[lesson.teacherId] || new Set();
    const groupBusy = state.groupBusy.get(lesson.groupId);
    const teacherBusy = state.teacherBusy.get(lesson.teacherId);
    const domain = [];
    for (const slot of allSlots) {
      const key = slotKey(slot.dia, slot.bloqueId);
      if (!availSet.has(key)) continue;
      if (groupBusy.has(key)) continue;
      if (teacherBusy.has(key)) continue;
      domain.push(slot);
    }
    return domain;
  }

  function orderDomain(domain, lesson, state, rnd) {
    const gsKey = `${lesson.groupId}|${lesson.subjectId}`;
    const usedDays = state.groupSubjectDay.get(gsKey);
    const preferred = [];
    const rest = [];
    for (const slot of domain) {
      if (usedDays.has(slot.dia)) rest.push(slot);
      else preferred.push(slot);
    }
    return [...shuffle(preferred, rnd), ...shuffle(rest, rnd)];
  }

  function applySlot(state, lesson, slot) {
    const key = slotKey(slot.dia, slot.bloqueId);
    state.groupBusy.get(lesson.groupId).add(key);
    state.teacherBusy.get(lesson.teacherId).add(key);
    const gsKey = `${lesson.groupId}|${lesson.subjectId}`;
    state.groupSubjectDay.get(gsKey).add(slot.dia);
    state.assignment.push({ ...lesson, dia: slot.dia, bloqueId: slot.bloqueId });
  }

  function undoSlot(state, lesson, slot) {
    const key = slotKey(slot.dia, slot.bloqueId);
    state.groupBusy.get(lesson.groupId).delete(key);
    state.teacherBusy.get(lesson.teacherId).delete(key);
    const gsKey = `${lesson.groupId}|${lesson.subjectId}`;
    state.assignment.pop();
    // No quitamos el día de groupSubjectDay a propósito: si más de una hora de la
    // misma materia terminó ese día, igual queremos evitarlo en próximos intentos,
    // pero como se recalcula el set entero por rama, lo reconstruimos abajo.
    state.groupSubjectDay.set(
      gsKey,
      new Set(
        state.assignment
          .filter((l) => l.groupId === lesson.groupId && l.subjectId === lesson.subjectId)
          .map((l) => l.dia)
      )
    );
  }

  function backtrack(remaining, state, rnd, budget) {
    if (remaining.length === 0) return { success: true };
    if (budget.count <= 0) return { success: false, aborted: true };
    budget.count -= 1;

    let chosenIdx = -1;
    let chosenDomain = null;
    for (let i = 0; i < remaining.length; i++) {
      const domain = computeDomain(remaining[i], state);
      if (chosenDomain === null || domain.length < chosenDomain.length) {
        chosenIdx = i;
        chosenDomain = domain;
        if (domain.length === 0) break;
      }
    }
    if (!chosenDomain || chosenDomain.length === 0) return { success: false };

    const lesson = remaining[chosenIdx];
    const newRemaining = remaining.slice(0, chosenIdx).concat(remaining.slice(chosenIdx + 1));
    const domainOrdered = orderDomain(chosenDomain, lesson, state, rnd);

    for (const slot of domainOrdered) {
      applySlot(state, lesson, slot);
      const result = backtrack(newRemaining, state, rnd, budget);
      if (result.success) return result;
      undoSlot(state, lesson, slot);
      if (result.aborted) return result;
    }
    return { success: false };
  }

  const maxAttempts = 40;
  const nodeBudgetPerAttempt = 20000;
  let finalAssignment = null;

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const rnd = mulberry32(attempt * 2654435761 + 12345);
    const state = {
      groupBusy: new Map(groups.map((g) => [g.id, new Set()])),
      teacherBusy: new Map(teachers.map((t) => [t.id, new Set()])),
      groupSubjectDay: new Map(),
      assignment: [],
    };
    for (const g of groups) {
      for (const a of g.asignaturas || []) {
        state.groupSubjectDay.set(`${g.id}|${a.subjectId}`, new Set());
      }
    }
    const order = shuffle(lessons, rnd);
    const budget = { count: nodeBudgetPerAttempt };
    const result = backtrack(order, state, rnd, budget);
    if (result.success) {
      finalAssignment = state.assignment;
      break;
    }
  }

  if (!finalAssignment) {
    return {
      success: false,
      error:
        "No fue posible generar un horario sin choques con los datos actuales. Revisa la disponibilidad de los profesores y la cantidad de horas asignadas.",
      warnings,
    };
  }

  const enriched = finalAssignment.map((l) => ({
    ...l,
    groupName: groupById[l.groupId]?.nombre || "",
    subjectName: subjectById[l.subjectId]?.nombre || "",
    teacherName: teacherById[l.teacherId]?.nombre || "",
  }));

  return {
    success: true,
    warnings,
    generatedAt: new Date().toISOString(),
    lessons: enriched,
  };
}
