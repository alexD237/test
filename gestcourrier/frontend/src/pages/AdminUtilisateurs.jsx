import { useEffect, useState } from "react";
import client from "../api/client";
import { PageHeader } from "../components/Layout";
import "./Admin.css";

const VIDE = { username: "", nom_complet: "", role: "AGENT", password: "" };

export default function AdminUtilisateurs() {
  const [liste, setListe] = useState([]);
  const [form, setForm] = useState(VIDE);
  const [erreur, setErreur] = useState("");
  const [succes, setSucces] = useState("");

  function charger() {
    client.get("/admin/utilisateurs/").then((res) => setListe(res.data.results || res.data));
  }

  useEffect(charger, []);

  async function creer(e) {
    e.preventDefault();
    setErreur("");
    setSucces("");
    try {
      await client.post("/admin/utilisateurs/", form);
      setSucces(`Compte ${form.username} créé.`);
      setForm(VIDE);
      charger();
    } catch (err) {
      const data = err.response?.data || {};
      setErreur(Object.values(data).flat().join(" ") || "Erreur lors de la création.");
    }
  }

  async function modifier(id, champs) {
    await client.patch(`/admin/utilisateurs/${id}/`, champs);
    charger();
  }

  async function reinitialiser(u) {
    const mdp = window.prompt(`Nouveau mot de passe pour ${u.username} :`);
    if (mdp) await modifier(u.id, { password: mdp });
  }

  return (
    <>
      <PageHeader title="Utilisateurs" />
      <div className="page">
        <form className="admin-form" onSubmit={creer}>
          <input
            className="mono"
            placeholder="Matricule (ex : 5487-T)"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />
          <input
            placeholder="Nom complet"
            value={form.nom_complet}
            onChange={(e) => setForm({ ...form, nom_complet: e.target.value })}
          />
          <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            <option value="AGENT">Agent</option>
            <option value="ADMIN">Administrateur</option>
          </select>
          <input
            type="password"
            placeholder="Mot de passe"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          <button className="btn btn-primary" type="submit">
            Créer le compte
          </button>
        </form>
        {succes && <p className="alert-succes">{succes}</p>}
        {erreur && <p className="field-error">{erreur}</p>}

        <table className="admin-table">
          <thead>
            <tr>
              <th>Matricule</th>
              <th>Nom</th>
              <th>Rôle</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {liste.map((u) => (
              <tr key={u.id} className={u.is_active ? "" : "inactif"}>
                <td className="mono">{u.username}</td>
                <td>{u.nom_complet}</td>
                <td>
                  <select value={u.role} onChange={(e) => modifier(u.id, { role: e.target.value })}>
                    <option value="AGENT">Agent</option>
                    <option value="ADMIN">Administrateur</option>
                  </select>
                </td>
                <td>
                  <span className={u.is_active ? "statut-actif" : "statut-inactif"}>
                    {u.is_active ? "Actif" : "Désactivé"}
                  </span>
                </td>
                <td className="admin-actions">
                  <button className="btn btn-ghost" onClick={() => modifier(u.id, { is_active: !u.is_active })}>
                    {u.is_active ? "Désactiver" : "Réactiver"}
                  </button>
                  <button className="btn btn-ghost" onClick={() => reinitialiser(u)}>
                    Réinitialiser le mot de passe
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
