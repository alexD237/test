import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import WaveDivider from "./WaveDivider";
import logo from "../assets/logo-pad.png";
import "./Layout.css";

const NAV = [
  { to: "/", label: "Registre", end: true },
  { to: "/depot", label: "Déposer un courrier" },
  { to: "/reporting", label: "Reporting" },
];

const NAV_ADMIN = [
  { to: "/admin/utilisateurs", label: "Utilisateurs" },
  { to: "/admin/audit", label: "Journal d'audit" },
  { to: "/admin/stats", label: "Statistiques" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const estAdmin = user?.role === "ADMIN";

  function onLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img src={logo} alt="Port Autonome de Douala" className="sidebar-logo" />
          <div>
            <span className="sidebar-eyebrow">PAD · DRH</span>
            <strong>GestCourrier</strong>
          </div>
        </div>
        <nav className="sidebar-nav">
          {NAV.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end}>
              {item.label}
            </NavLink>
          ))}
          {estAdmin && (
            <>
              <span className="sidebar-section">Administration</span>
              {NAV_ADMIN.map((item) => (
                <NavLink key={item.to} to={item.to}>
                  {item.label}
                </NavLink>
              ))}
            </>
          )}
        </nav>
        <div className="sidebar-profile">
          <div>
            <strong>{user?.nom_complet}</strong>
            <span className="sidebar-role">{user?.role}</span>
          </div>
          <button className="btn btn-ghost sidebar-logout" onClick={onLogout}>
            Déconnexion
          </button>
        </div>
        <WaveDivider className="sidebar-wave" />
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}

export function PageHeader({ title, actions }) {
  return (
    <header className="topbar">
      <h1>{title}</h1>
      {actions && <div className="topbar-actions">{actions}</div>}
    </header>
  );
}
