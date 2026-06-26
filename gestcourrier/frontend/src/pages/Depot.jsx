import { useState } from "react";
import { useNavigate } from "react-router-dom";
import client from "../api/client";
import { PageHeader } from "../components/Layout";
import ChampAutocomplete from "../components/ChampAutocomplete";
import "./Depot.css";

const aujourdhui = new Date().toISOString().slice(0, 10);

const VIDE = {
  numero: "",
  type_courrier: "ENTRANT",
  date_courrier: aujourdhui,
  correspondant: "",
  service_interne: "",
  signataire: "",
  objet: "",
  annotations_directeur: "",
  observation: "",
};

export default function Depot() {
  const navigate = useNavigate();
  const [form, setForm] = useState(VIDE);
  const [fichier, setFichier] = useState(null);
  const [erreurs, setErreurs] = useState({});
  const [enCours, setEnCours] = useState(false);

  const entrant = form.type_courrier === "ENTRANT";

  function set(champ, valeur) {
    setForm((f) => ({ ...f, [champ]: valeur }));
  }

  const numeroValide = /^\d{6}-\d{2}$/.test(form.numero);
  const complet =
    numeroValide &&
    form.correspondant &&
    form.objet &&
    fichier &&
    (entrant ? form.service_interne : form.signataire);

  async function onSubmit(e) {
    e.preventDefault();
    setErreurs({});
    setEnCours(true);
    const payload = new FormData();
    payload.append("numero", form.numero);
    payload.append("type_courrier", form.type_courrier);
    payload.append("date_courrier", form.date_courrier);
    payload.append("correspondant", form.correspondant);
    payload.append("objet", form.objet);
    payload.append("observation", form.observation);
    payload.append("fichier_pdf", fichier);
    if (entrant) {
      payload.append("service_interne", form.service_interne);
      payload.append("annotations_directeur", form.annotations_directeur);
    } else {
      payload.append("signataire", form.signataire);
    }
    try {
      await client.post("/courriers/", payload);
      navigate("/");
    } catch (err) {
      setErreurs(err.response?.data || { detail: "Erreur lors du dépôt." });
    } finally {
      setEnCours(false);
    }
  }

  return (
    <>
      <PageHeader title="Déposer un courrier" />
      <div className="page">
        <form className="depot-form" onSubmit={onSubmit}>
          <div className="depot-type">
            {["ENTRANT", "SORTANT"].map((t) => (
              <label key={t} className={form.type_courrier === t ? "actif" : ""}>
                <input
                  type="radio"
                  name="type"
                  checked={form.type_courrier === t}
                  onChange={() => set("type_courrier", t)}
                />
                {t === "ENTRANT" ? "Courrier entrant" : "Courrier sortant"}
              </label>
            ))}
          </div>

          <div className="depot-grid">
            <div className="field">
              <label htmlFor="numero">Numéro de courrier *</label>
              <input
                id="numero"
                className="mono"
                value={form.numero}
                onChange={(e) => set("numero", e.target.value)}
                placeholder="004901-26"
              />
              {form.numero && !numeroValide && (
                <span className="field-error">Format attendu : XXXXXX-AA</span>
              )}
              {erreurs.numero && <span className="field-error">{erreurs.numero}</span>}
            </div>

            <div className="field">
              <label htmlFor="date">
                {entrant ? "Date de réception *" : "Date d'émission *"}
              </label>
              <input
                id="date"
                type="date"
                value={form.date_courrier}
                onChange={(e) => set("date_courrier", e.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="correspondant">
                {entrant ? "Expéditeur *" : "Destinataire *"}
              </label>
              <ChampAutocomplete
                champ="correspondant"
                id="correspondant"
                value={form.correspondant}
                onChange={(e) => set("correspondant", e.target.value)}
              />
            </div>

            {entrant ? (
              <div className="field">
                <label htmlFor="service">Service destinataire *</label>
                <ChampAutocomplete
                  champ="service_interne"
                  id="service"
                  value={form.service_interne}
                  onChange={(e) => set("service_interne", e.target.value)}
                />
              </div>
            ) : (
              <div className="field">
                <label htmlFor="signataire">Signataire *</label>
                <ChampAutocomplete
                  champ="signataire"
                  id="signataire"
                  value={form.signataire}
                  onChange={(e) => set("signataire", e.target.value)}
                />
              </div>
            )}
          </div>

          <div className="field">
            <label htmlFor="objet">Objet * ({form.objet.length}/300)</label>
            <input
              id="objet"
              maxLength={300}
              value={form.objet}
              onChange={(e) => set("objet", e.target.value)}
            />
          </div>

          {entrant && (
            <div className="field">
              <label htmlFor="annotations">Annotations du directeur</label>
              <textarea
                id="annotations"
                rows={3}
                value={form.annotations_directeur}
                onChange={(e) => set("annotations_directeur", e.target.value)}
              />
            </div>
          )}

          <div className="field">
            <label htmlFor="observation">Observation</label>
            <textarea
              id="observation"
              rows={2}
              value={form.observation}
              onChange={(e) => set("observation", e.target.value)}
            />
          </div>

          <div className="field">
            <label>Fichier PDF * (20 Mo max)</label>
            <label className="depot-upload">
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setFichier(e.target.files[0] || null)}
              />
              {fichier ? (
                <span className="mono">{fichier.name}</span>
              ) : (
                <span>Cliquez pour sélectionner le PDF numérisé</span>
              )}
            </label>
            {erreurs.fichier_pdf && (
              <span className="field-error">{erreurs.fichier_pdf}</span>
            )}
          </div>

          {erreurs.detail && <p className="field-error">{erreurs.detail}</p>}

          <button type="submit" className="btn btn-primary" disabled={!complet || enCours}>
            {enCours ? "Enregistrement…" : "Enregistrer le courrier"}
          </button>
        </form>
      </div>
    </>
  );
}
