const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Error ${res.status}`);
  }
  return res.json();
}

export const api = {
  getConfig: () => request("/config"),
  updateConfig: (data) => request("/config", { method: "PUT", body: JSON.stringify(data) }),

  listSubjects: () => request("/subjects"),
  createSubject: (data) => request("/subjects", { method: "POST", body: JSON.stringify(data) }),
  updateSubject: (id, data) => request(`/subjects/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteSubject: (id) => request(`/subjects/${id}`, { method: "DELETE" }),

  listTeachers: () => request("/teachers"),
  createTeacher: (data) => request("/teachers", { method: "POST", body: JSON.stringify(data) }),
  updateTeacher: (id, data) => request(`/teachers/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteTeacher: (id) => request(`/teachers/${id}`, { method: "DELETE" }),

  listGroups: () => request("/groups"),
  createGroup: (data) => request("/groups", { method: "POST", body: JSON.stringify(data) }),
  updateGroup: (id, data) => request(`/groups/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteGroup: (id) => request(`/groups/${id}`, { method: "DELETE" }),

  getSchedule: () => request("/schedule"),
  generateSchedule: () => request("/schedule/generate", { method: "POST" }),
};
