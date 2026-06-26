import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";
import client from "../api/client";
import { PageHeader } from "../components/Layout";
import "./Fiche.css";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

export default function Fiche() {
  const { id } = useParams();
  const [courrier, setCourrier] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [pages, setPages] = useState(0);
  const [erreur, setErreur] = useState("");

  useEffect(() => {
    client.get(`/courriers/${id}/`).then((res) => setCourrier(res.data)).catch(() => setErreur("Courrier introuvable."));
  }, [id]);

  useEffect(() => {
    let url;
    client
      .get(`/courriers/${id}/pdf/`, { responseType: "blob" })
      .then((res) => {
        url = URL.createObjectURL(res.data);
        setPdfUrl(url);
      });
    return () => url && URL.revokeObjectURL(url);
  }, [id]);

  async function telecharger() {
    const res = await client.get(`/courriers/${id}/pdf/`, { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${courrier.numero}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (erreur) return <div className="page">{erreur}</div>;
  if (!courrier) return <div className="page">Chargement…</div>;

  const entrant = courrier.type_courrier === "ENTRANT";

  return (
    <>
      <PageHeader
        title={courrier.numero}
        actions={
          <button className="btn btn-accent" onClick={telecharger}>
            Télécharger le PDF
          </button>
        }
      />
      <div className="page fiche">
        <nav className="fil-ariane">
          <Link to="/">Registre</Link> <span>→</span> <span className="mono">{courrier.numero}</span>
        </nav>

        <div className="fiche-grid">
          <section className="fiche-meta">
            <span className={`badge badge-${courrier.type_courrier.toLowerCase()}`}>
              {entrant ? "Entrant" : "Sortant"}
            </span>
            <dl>
              <dt>{entrant ? "Date de réception" : "Date d'émission"}</dt>
              <dd>{courrier.date_courrier}</dd>
              <dt>{entrant ? "Expéditeur" : "Destinataire"}</dt>
              <dd>{courrier.correspondant}</dd>
              {entrant ? (
                <>
                  <dt>Service destinataire</dt>
                  <dd>{courrier.service_interne}</dd>
                </>
              ) : (
                <>
                  <dt>Signataire</dt>
                  <dd>{courrier.signataire}</dd>
                </>
              )}
              <dt>Objet</dt>
              <dd>{courrier.objet}</dd>
              {entrant && courrier.annotations_directeur && (
                <>
                  <dt>Annotations du directeur</dt>
                  <dd>{courrier.annotations_directeur}</dd>
                </>
              )}
              {courrier.observation && (
                <>
                  <dt>Observation</dt>
                  <dd>{courrier.observation}</dd>
                </>
              )}
            </dl>
          </section>

          <section className="fiche-pdf">
            {pdfUrl ? (
              <Document
                file={pdfUrl}
                onLoadSuccess={({ numPages }) => setPages(numPages)}
                loading="Chargement du PDF…"
                error="Impossible d'afficher le PDF."
              >
                {Array.from({ length: pages }, (_, i) => (
                  <Page key={i} pageNumber={i + 1} width={620} />
                ))}
              </Document>
            ) : (
              <p>Chargement du PDF…</p>
            )}
          </section>
        </div>
      </div>
    </>
  );
}
