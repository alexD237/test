import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { PageHeader } from "../components/Layout";
import "./Registre.css";

export default function Registre() {
  const navigate = useNavigate();
  const [data, setData] = useState({ results: [], count: 0 });
  const [page, setPage] = useState(1);
  const [chargement, setChargement] = useState(true);

  useEffect(() => {
    setChargement(true);
    client
      .get("/courriers/", { params: { page } })
      .then((res) => setData(res.data))
      .finally(() => setChargement(false));
  }, [page]);

  const totalPages = Math.max(1, Math.ceil(data.count / 20));

  return (
    <>
      <PageHeader
        title="Registre des courriers"
        actions={
          <button className="btn btn-primary" onClick={() => navigate("/depot")}>
            + Déposer un courrier
          </button>
        }
      />
      <div className="page">
        {chargement ? (
          <p>Chargement…</p>
        ) : data.count === 0 ? (
          <p className="registre-vide">Aucun courrier enregistré.</p>
        ) : (
          <>
            <table className="registre">
              <thead>
                <tr>
                  <th>Numéro</th>
                  <th>Type</th>
                  <th>Date</th>
                  <th>Correspondant</th>
                  <th>Objet</th>
                  <th>PDF</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((c) => (
                  <tr key={c.id}>
                    <td className="mono">{c.numero}</td>
                    <td>
                      <span className={`badge badge-${c.type_courrier.toLowerCase()}`}>
                        {c.type_courrier === "ENTRANT" ? "Entrant" : "Sortant"}
                      </span>
                    </td>
                    <td>{c.date_courrier}</td>
                    <td>{c.correspondant}</td>
                    <td className="registre-objet">{c.objet}</td>
                    <td>{c.fichier_pdf ? "✓" : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="pagination">
              <button
                className="btn btn-ghost"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Précédent
              </button>
              <span>
                Page {page} / {totalPages} · {data.count} résultat(s)
              </span>
              <button
                className="btn btn-ghost"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Suivant
              </button>
            </div>
          </>
        )}
      </div>
    </>
  );
}
