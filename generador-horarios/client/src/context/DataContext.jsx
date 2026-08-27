import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "../api";

const DataContext = createContext(null);

export function DataProvider({ children }) {
  const [config, setConfig] = useState({ dias: [], bloques: [] });
  const [subjects, setSubjects] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [c, s, t, g] = await Promise.all([
        api.getConfig(),
        api.listSubjects(),
        api.listTeachers(),
        api.listGroups(),
      ]);
      setConfig(c);
      setSubjects(s);
      setTeachers(t);
      setGroups(g);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  return (
    <DataContext.Provider value={{ config, subjects, teachers, groups, loading, error, reload }}>
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error("useData debe usarse dentro de DataProvider");
  return ctx;
}
