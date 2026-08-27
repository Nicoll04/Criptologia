# Generador de Horarios Escolares

Aplicación web para generar horarios de clase de un colegio, evitando
choques entre profesores, grupos y respetando la disponibilidad y el
tiempo pedagógico de cada docente.

- **Backend**: Node.js + Express (API REST, almacenamiento en archivo JSON).
- **Frontend**: React + Vite.

## Funcionalidades

- Gestión de **materias**, **profesores** (con las materias que dictan,
  su disponibilidad semanal y sus horas de tiempo pedagógico) y
  **grupos/cursos** (con la carga académica: materia + profesor + horas
  semanales).
- Configuración de los días y bloques horarios del colegio.
- Generación automática del horario con un algoritmo de backtracking
  (tipo CSP) que garantiza:
  - Ningún profesor ni grupo queda en dos clases al mismo tiempo.
  - Solo se usan los bloques en que el profesor está disponible.
  - La carga de horas de cada profesor nunca supera su disponibilidad
    menos el tiempo pedagógico que debe quedar libre.
  - Se evita repetir la misma materia el mismo día para un grupo cuando
    es posible.
- Visualización del horario resultante por **grupo** y por **profesor**.

## Cómo correrlo

### 1. Backend

```bash
cd server
npm install
npm run dev   # http://localhost:4000
```

Los datos se guardan en `server/data/db.json` (se crea automáticamente).

### 2. Frontend

En otra terminal:

```bash
cd client
npm install
npm run dev   # http://localhost:5173
```

El frontend usa un proxy (`vite.config.js`) hacia `http://localhost:4000`
para las peticiones a `/api`, así que el backend debe estar corriendo.

## Flujo de uso sugerido

1. **Configuración**: define los días de clase y los bloques horarios.
2. **Materias**: registra las asignaturas del colegio.
3. **Profesores**: agrega cada profesor, las materias que dicta, su
   disponibilidad semanal y sus horas de tiempo pedagógico.
4. **Grupos**: crea cada grupo/curso y arma su carga académica (materia,
   profesor y horas semanales).
5. **Horario**: pulsa "Generar horario" y consulta el resultado por
   grupo o por profesor.

Si la generación falla, la app muestra el motivo (por ejemplo, un
profesor con más horas asignadas que disponibilidad).
