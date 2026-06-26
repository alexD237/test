import { useEffect, useId, useState } from "react";
import client from "../api/client";

// Champ texte libre avec suggestions issues de l'historique des courriers
// (datalist natif : l'utilisateur reste libre de saisir une nouvelle valeur).
export default function ChampAutocomplete({ champ, ...props }) {
  const listId = useId();
  const [options, setOptions] = useState([]);

  useEffect(() => {
    let actif = true;
    client
      .get("/courriers/suggestions/", { params: { champ } })
      .then((res) => actif && setOptions(res.data))
      .catch(() => {});
    return () => {
      actif = false;
    };
  }, [champ]);

  return (
    <>
      <input list={listId} autoComplete="off" {...props} />
      <datalist id={listId}>
        {options.map((o) => (
          <option key={o} value={o} />
        ))}
      </datalist>
    </>
  );
}
