// Indicateur de chargement (anneau or PAD).
export default function Spinner({ texte = "Chargement…" }) {
  return (
    <div className="chargement">
      <span className="spinner" aria-hidden="true" />
      <span>{texte}</span>
    </div>
  );
}
