import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import client from "../api/client";
import { PageHeader } from "../components/Layout";
import ChampAutocomplete from "../components/ChampAutocomplete";
import Spinner from "../components/Spinner";
import "./Registre.css";

const FILTRES_VIDES = {
  q: "",
  type: "",
  numero: "",
  service: "",
  signataire: "",
  date_debut: "",
  date_fin: "",
  avec_pdf: "",
};

export default function Registre() {
  const navigate = useNavigate();
  const [data, setData] = useState({ results: [], count: 0 });
  const [page, setPage] = useState(1);
  const [tri, setTri] = useState("-date");
  const [filtres, setFiltres] = useState(FILTRES_VIDES);
  const [chargement, setChargement] = useState(true);

  useEffect(() => {
    const params = { page, tri };
    Object.entries(filtres).forEach(([k, v]) => v && (params[k] = v));
    setChargement(true);
    client
      .get("/courriers/", { params })
      .then((res) => setData(res.data))
      .finally(() => setChargement(false));
  }, [page, tri, filtres]);

  function setFiltre(champ, valeur) {
    setPage(1);
    setFiltres((f) => ({ ...f, [champ]: valeur }));
  }

  function changerTri(colonne) {
    setTri((t) => (t === colonne ? `-${colonne}` : colonne));
  }

  function enTete(colonne, libelle) {
    const actif = tri.replace("-", "") === colonne;
    return (
      <th className={actif ? "tri actif" : "tri"} onClick={() => changerTri(colonne)}>
        {libelle}
        {actif && <span className="fleche">{tri.startsWith("-") ? "▼" : "▲"}</span>}
      </th>
    );
  }

  const totalPages = Math.max(1, Math.ceil(data.count / 20));
  const entrant = filtres.type !== "SORTANT";

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
        <div className="filtres">
          <input
            className="filtres-recherche"
            placeholder="Rechercher (objet, correspondant, annotations…)"
            value={filtres.q}
            onChange={(e) => setFiltre("q", e.target.value)}
          />
          <select value={filtres.type} onChange={(e) => setFiltre("type", e.target.value)}>
            <option value="">Tous les types</option>
            <option value="ENTRANT">Entrant</option>
            <option value="SORTANT">Sortant</option>
          </select>
          <input
            className="mono"
            placeholder="N° courrier"
            value={filtres.numero}
            onChange={(e) => setFiltre("numero", e.target.value)}
          />
          {entrant ? (
            <ChampAutocomplete
              champ="service_interne"
              placeholder="Tout service"
              value={filtres.service}
              onChange={(e) => setFiltre("service", e.target.value)}
            />
          ) : (
            <ChampAutocomplete
              champ="signataire"
              placeholder="Tout signataire"
              value={filtres.signataire}
              onChange={(e) => setFiltre("signataire", e.target.value)}
            />
          )}
          <input
            type="date"
            title="Date début"
            value={filtres.date_debut}
            onChange={(e) => setFiltre("date_debut", e.target.value)}
          />
          <input
            type="date"
            title="Date fin"
            value={filtres.date_fin}
            onChange={(e) => setFiltre("date_fin", e.target.value)}
          />
          <select value={filtres.avec_pdf} onChange={(e) => setFiltre("avec_pdf", e.target.value)}>
            <option value="">PDF : tous</option>
            <option value="true">Avec PDF</option>
            <option value="false">Sans PDF</option>
          </select>
          <button
            className="btn btn-ghost"
            onClick={() => {
              setPage(1);
              setFiltres(FILTRES_VIDES);
            }}
          >
            Réinitialiser
          </button>
        </div>

        {chargement ? (
          <Spinner />
        ) : data.count === 0 ? (
          <p className="registre-vide">Aucun courrier ne correspond.</p>
        ) : (
          <>
            <table className="registre">
              <thead>
                <tr>
                  {enTete("numero", "Numéro")}
                  <th>Type</th>
                  {enTete("date", "Date")}
                  <th>Correspondant</th>
                  <th>Objet</th>
                  <th>PDF</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((c) => (
                  <tr key={c.id}>
                    <td className="mono">
                      <Link to={`/courriers/${c.id}`}>{c.numero}</Link>
                    </td>
                    <td>
                      <span className={`badge badge-${c.type_courrier.toLowerCase()}`}>
                        {c.type_courrier === "ENTRANT" ? "Entrant" : "Sortant"}
                      </span>
                    </td>
                    <td>{c.date_courrier}</td>
                    <td>{c.correspondant}</td>
                    <td className="registre-objet">{c.objet}</td>
                    <td>{c.fichier_pdf ? <span className="pdf-oui">✓</span> : "—"}</td>
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
