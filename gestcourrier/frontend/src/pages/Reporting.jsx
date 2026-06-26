import { useEffect, useState } from "react";
import client from "../api/client";
import { PageHeader } from "../components/Layout";
import BarChart from "../components/BarChart";
import Spinner from "../components/Spinner";
import "./Reporting.css";

function moisActuel() {
  return new Date().toISOString().slice(0, 7);
}

export default function Reporting() {
  const [mois, setMois] = useState(moisActuel());
  const [data, setData] = useState(null);
  const [chargement, setChargement] = useState(true);

  useEffect(() => {
    setChargement(true);
    client.get("/reporting/mensuel/", { params: { mois } }).then((res) => setData(res.data)).finally(() => setChargement(false));
  }, [mois]);

  async function exporterPdf() {
    const res = await client.get("/reporting/export-pdf/", { params: { mois }, responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `rapport-${mois}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <>
      <PageHeader
        title="Reporting mensuel"
        actions={
          <button className="btn btn-accent" onClick={exporterPdf} disabled={!data?.total}>
            Exporter en PDF
          </button>
        }
      />
      <div className="page">
        <input
          type="month"
          className="reporting-mois"
          value={mois}
          onChange={(e) => setMois(e.target.value)}
        />

        {chargement ? (
          <Spinner />
        ) : (
          <>
            <div className="reporting-chiffres">
              <div className="reporting-chiffre">
                <span className="valeur">{data.total}</span>
                <span className="label">Courriers traités</span>
              </div>
              <div className="reporting-chiffre">
                <span className="valeur">{data.total_entrants}</span>
                <span className="label">Entrants</span>
              </div>
              <div className="reporting-chiffre">
                <span className="valeur">{data.total_sortants}</span>
                <span className="label">Sortants</span>
              </div>
              <div className="reporting-chiffre">
                <span className="valeur">{data.taux_numerise}%</span>
                <span className="label">Numérisés (avec PDF)</span>
              </div>
            </div>

            <section className="reporting-graphe">
              <h2>Volume hebdomadaire (entrants / sortants)</h2>
              <BarChart data={data.par_semaine} />
            </section>

            <div className="reporting-tables">
              <section>
                <h2>Entrants par service destinataire</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Service</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.par_service.length === 0 ? (
                      <tr>
                        <td colSpan={2}>Aucun courrier entrant ce mois-ci.</td>
                      </tr>
                    ) : (
                      data.par_service.map((l) => (
                        <tr key={l.service_interne}>
                          <td>{l.service_interne}</td>
                          <td>{l.total}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </section>

              <section>
                <h2>Sortants par signataire</h2>
                <table>
                  <thead>
                    <tr>
                      <th>Signataire</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.par_signataire.length === 0 ? (
                      <tr>
                        <td colSpan={2}>Aucun courrier sortant ce mois-ci.</td>
                      </tr>
                    ) : (
                      data.par_signataire.map((l) => (
                        <tr key={l.signataire}>
                          <td>{l.signataire}</td>
                          <td>{l.total}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </section>
            </div>
          </>
        )}
      </div>
    </>
  );
}
