import { NavLink, Route, Routes } from "react-router-dom";
import { DataProvider } from "./context/DataContext";
import Materias from "./pages/Materias";
import Profesores from "./pages/Profesores";
import Grupos from "./pages/Grupos";
import Horario from "./pages/Horario";
import Configuracion from "./pages/Configuracion";

function App() {
  return (
    <DataProvider>
      <div className="app-shell">
        <header className="app-header">
          <h2>Generador de Horarios</h2>
          <nav>
            <NavLink to="/" end>
              Horario
            </NavLink>
            <NavLink to="/materias">Materias</NavLink>
            <NavLink to="/profesores">Profesores</NavLink>
            <NavLink to="/grupos">Grupos</NavLink>
            <NavLink to="/configuracion">Configuración</NavLink>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Horario />} />
            <Route path="/materias" element={<Materias />} />
            <Route path="/profesores" element={<Profesores />} />
            <Route path="/grupos" element={<Grupos />} />
            <Route path="/configuracion" element={<Configuracion />} />
          </Routes>
        </main>
      </div>
    </DataProvider>
  );
}

export default App;
