import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import logo from "../assets/logo-pad.png";
import "./Login.css";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [erreur, setErreur] = useState("");
  const [enCours, setEnCours] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setErreur("");
    setEnCours(true);
    try {
      await login(username, password);
      navigate("/", { replace: true });
    } catch {
      setErreur("Matricule ou mot de passe incorrect.");
    } finally {
      setEnCours(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={onSubmit}>
        <img src={logo} alt="Port Autonome de Douala" className="login-logo" />
        <h1>GestCourrier DRH</h1>
        <p className="login-sub">Numérisation et archivage des courriers</p>

        <div className="field">
          <label htmlFor="username">Matricule</label>
          <input
            id="username"
            className="mono"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="5487-T"
            autoFocus
          />
        </div>
        <div className="field">
          <label htmlFor="password">Mot de passe</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {erreur && <p className="field-error">{erreur}</p>}

        <button
          type="submit"
          className="btn btn-primary"
          disabled={!username || !password || enCours}
        >
          {enCours ? "Connexion…" : "Se connecter"}
        </button>
      </form>
    </div>
  );
}
