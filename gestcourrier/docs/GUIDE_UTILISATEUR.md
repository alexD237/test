# Guide utilisateur — ArchivRH

Application de numérisation et d'archivage du courrier du Bureau Courrier de la
Direction des Ressources Humaines (Port Autonome de Douala).

## 1. Connexion

1. Ouvrir l'application depuis l'intranet DRH.
2. Saisir votre **matricule** (ex. `5487-T`) et votre **mot de passe**.
3. Cliquer sur **Se connecter**.

> Après 5 tentatives échouées, le compte est verrouillé 15 minutes.
> Une session inactive pendant 30 minutes est déconnectée automatiquement.

Les comptes sont créés par l'administrateur ; il n'y a pas d'auto-inscription.

## 2. Déposer un courrier

Menu **Déposer un courrier**.

1. Choisir le type : **Entrant** (reçu) ou **Sortant** (émis).
2. Renseigner :
   - **Numéro** au format `XXXXXX-AA` (ex. `004901-26`).
   - **Date**, **expéditeur/destinataire**, **objet**.
   - Pour un entrant : **service destinataire** (et éventuelles annotations).
   - Pour un sortant : **signataire**.
3. Joindre le **PDF numérisé** (20 Mo maximum).
4. **Enregistrer le courrier**.

## 3. Consulter et rechercher

Menu **Registre**.

- **Recherche plein texte** : objet, correspondant, annotations, observation.
- **Filtres** : type, numéro, service ou signataire, plage de dates, présence de PDF.
- **Tri** : cliquer sur les colonnes Numéro ou Date.
- Cliquer sur un **numéro** pour ouvrir la fiche du courrier.

### Fiche courrier

Affiche toutes les métadonnées et le **PDF intégré** (lecture sans plugin).
Bouton **Télécharger le PDF** pour récupérer le fichier.

## 4. Reporting mensuel

Menu **Reporting**.

- Sélectionner le mois.
- Visualiser : volumes traités, entrants/sortants, taux de numérisation,
  répartition par service et par signataire.
- **Exporter en PDF** pour le rapport mensuel mis en page aux couleurs PAD.

## 5. Administration (réservé aux administrateurs)

Section **Administration** de la barre latérale.

- **Utilisateurs** : créer un compte (matricule + mot de passe), changer un rôle,
  désactiver/réactiver, réinitialiser un mot de passe.
- **Journal d'audit** : historique horodaté de toutes les actions (connexion,
  dépôt, consultation, téléchargement, modification, suppression). Filtrable par
  action et par agent, **exportable en CSV**. Les entrées sont immuables.
- **Statistiques système** : nombre de fichiers, espace utilisé, taille moyenne,
  espace disque libre.

## 6. Rôles

| Rôle | Droits |
|------|--------|
| **Agent** | Déposer, consulter, rechercher, télécharger, reporting |
| **Administrateur** | Tout l'agent + gestion des comptes, audit, statistiques, suppression |

> La suppression d'un courrier est **logique** (réservée à l'administrateur) :
> le document reste archivé mais n'apparaît plus dans le registre.
