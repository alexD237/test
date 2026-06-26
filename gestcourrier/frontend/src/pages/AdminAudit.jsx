import { useEffect, useState } from "react";
import client from "../api/client";
import { PageHeader } from "../components/Layout";
import "./Admin.css";

const ACTIONS = [
  "DEPOT", "CONSULTATION", "TELECHARGEMENT", "MODIFICATION", "SUPPRESSION", "CONNEXION", "ADMIN",
];

export default function AdminAudit() {
  const [data, setData] = useState({ results: [], count: 0 });
  const [page, setPage] = useState(1);
  const [filtres, setFiltres] = useState({ action: "", utilisateur: "" });

  useEffect(() => {
    const params = { page };
    if (filtres.action) params.action = filtres.action;
    if (filtres.utilisateur) params.utilisateur = filtres.utilisateur;
    client.get("/admin/audit/", { params }).then((res) => setData(res.data));
  }, [page, filtres]);

  function setFiltre(champ, valeur) {
    setPage(1);
    setFiltres((f) => ({ ...f, [champ]: valeur }));
  }

  async function exporterCsv() {
    const params = {};
    if (filtres.action) params.action = filtres.action;
    if (filtres.utilisateur) params.utilisateur = filtres.utilisateur;
    const res = await client.get("/admin/audit/export-csv/", { params, responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = "journal-audit.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  const totalPages = Math.max(1, Math.ceil(data.count / 20));

  return (
    <>
      <PageHeader
        title="Journal d'audit"
        actions={
          <button className="btn btn-accent" onClick={exporterCsv}>
            Exporter en CSV
          </button>
        }
      />
      <div className="page">
        <div className="filtres">
          <select value={filtres.action} onChange={(e) => setFiltre("action", e.target.value)}>
            <option value="">Toutes les actions</option>
            {ACTIONS.map((a) => (
              <option key={a}>{a}</option>
            ))}
          </select>
          <input
            className="mono"
            placeholder="Matricule de l'agent"
            value={filtres.utilisateur}
            onChange={(e) => setFiltre("utilisateur", e.target.value)}
          />
        </div>

        <table className="admin-table">
          <thead>
            <tr>
              <th>Horodatage (UTC)</th>
              <th>Agent</th>
              <th>Action</th>
              <th>Courrier</th>
              <th>Détail</th>
              <th>IP</th>
            </tr>
          </thead>
          <tbody>
            {data.results.map((l) => (
              <tr key={l.id}>
                <td>{new Date(l.horodatage).toISOString().slice(0, 19).replace("T", " ")}</td>
                <td className="mono">{l.utilisateur}</td>
                <td>
                  <span className="badge">{l.action}</span>
                </td>
                <td className="mono">{l.numero || "—"}</td>
                <td>{l.detail || "—"}</td>
                <td className="mono">{l.adresse_ip || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="pagination">
          <button className="btn btn-ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            Précédent
          </button>
          <span>
            Page {page} / {totalPages} · {data.count} entrée(s)
          </span>
          <button className="btn btn-ghost" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
            Suivant
          </button>
        </div>
      </div>
    </>
  );
}
