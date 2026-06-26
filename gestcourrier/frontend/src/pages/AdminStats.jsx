import { useEffect, useState } from "react";
import client from "../api/client";
import { PageHeader } from "../components/Layout";
import "./Admin.css";
import "./Reporting.css";

function octets(n) {
  if (n >= 1e9) return `${(n / 1e9).toFixed(2)} Go`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(2)} Mo`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)} Ko`;
  return `${n} o`;
}

export default function AdminStats() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    client.get("/admin/stats-systeme/").then((res) => setStats(res.data));
  }, []);

  if (!stats) return <div className="page">Chargement…</div>;

  const cartes = [
    { valeur: stats.nombre_fichiers, label: "Fichiers PDF stockés" },
    { valeur: octets(stats.espace_utilise_octets), label: "Espace utilisé" },
    { valeur: octets(stats.taille_moyenne_octets), label: "Taille moyenne / document" },
    { valeur: octets(stats.disque_libre_octets), label: "Espace disque libre" },
  ];

  return (
    <>
      <PageHeader title="Statistiques système" />
      <div className="page">
        <div className="reporting-chiffres">
          {cartes.map((c) => (
            <div className="reporting-chiffre" key={c.label}>
              <span className="valeur">{c.valeur}</span>
              <span className="label">{c.label}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
