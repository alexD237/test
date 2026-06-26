import { useEffect, useRef } from "react";

// Déconnexion automatique après 30 minutes d'inactivité (CDC 5.1).
const DELAI_MS = 30 * 60 * 1000;
const EVENEMENTS = ["mousemove", "keydown", "click", "scroll", "touchstart"];

export default function useInactivityLogout(surExpiration) {
  const callback = useRef(surExpiration);
  callback.current = surExpiration;

  useEffect(() => {
    let minuteur;
    function rearmer() {
      clearTimeout(minuteur);
      minuteur = setTimeout(() => callback.current(), DELAI_MS);
    }
    EVENEMENTS.forEach((e) => window.addEventListener(e, rearmer));
    rearmer();
    return () => {
      clearTimeout(minuteur);
      EVENEMENTS.forEach((e) => window.removeEventListener(e, rearmer));
    };
  }, []);
}
