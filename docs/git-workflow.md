# Guide Git / GitHub — DVF Île-de-France

Commandes destinées à **PowerShell sous Windows**, dans le dossier racine du projet.
GitHub ne reçoit aucun code tant que tu n'exécutes pas les commandes de push.

## Étape 1 — Premier dépôt local

```powershell
git --version
git config --global user.name "Ton Nom"
git config --global user.email "ton.email@example.com"
git init -b main
git add .
git status
git commit -m "chore: initialiser le projet DVF IDF"
```

Avant `git add .`, vérifier que `.env`, `data/raw/*.csv.gz` et les autres données
sensibles ne seront pas ajoutés (`git status --short`).

## Étape 2 — Dépôt GitHub distant

### Option A : GitHub CLI (`gh`) installé

```powershell
gh auth login
gh repo create dvf-idf-analytics --public --source . --remote origin --push
```

`gh auth login` ouvre une authentification sécurisée ; ne colle jamais de mot de
passe ni de token personnel dans un script ou une conversation.

### Option B : site GitHub

Créer **un dépôt vide** nommé `dvf-idf-analytics` sur github.com/new, SANS cocher
« Add a README », puis :

```powershell
git remote add origin https://github.com/TON_PSEUDO/dvf-idf-analytics.git
git push -u origin main
```

Remplacer `TON_PSEUDO`. Si un dépôt distant existe déjà, vérifier son historique
avant de changer les branches ou de faire un push.

## Étape 3 — Branche d'intégration

```powershell
git switch -c develop
git push -u origin develop
```

Dans GitHub, définir `main` comme branche protégée et demander des Pull Requests ;
on peut aussi protéger `develop` après la première PR.

## Étape 4 — Première branche de fonctionnalité

```powershell
git switch develop
git pull --ff-only origin develop
git switch -c feature/etl-improvements
```

Modifier un vrai fichier et ajouter une amélioration testable (par exemple un
contrôle qualité ou un test). Puis :

```powershell
git status
git add .
git commit -m "test: renforcer les controles du pipeline DVF"
git push -u origin feature/etl-improvements
```

## Étape 5 — Pull Request et fusion

Avec GitHub CLI :

```powershell
gh pr create --base develop --head feature/etl-improvements --title "Tests ETL DVF" --body "Renforcement des controles de donnees et tests"
```

Ou bien : GitHub > Pull requests > New pull request > base `develop`, compare
`feature/etl-improvements`.

Attendre le résultat **vert** de CI, relire les changements, puis faire « Squash
and merge ». Avec GitHub CLI :

```powershell
gh pr merge --squash --delete-branch
```

Se remettre à jour localement :

```powershell
git switch develop
git pull --ff-only origin develop
git branch -d feature/etl-improvements
```

## Étape 6 — Livraison vers main

Créer une Pull Request de `develop` vers `main` sur GitHub, valider la CI, puis
fusionner. Ce processus garantit que `main` reste présentable.

## Commandes à connaître

| Commande | Utilité |
|---|---|
| `git status` | Voir les changements locaux |
| `git switch -c feature/nom` | Créer et ouvrir une branche |
| `git add .` | Préparer les fichiers suivis/non ignorés |
| `git commit -m "message"` | Enregistrer un commit local |
| `git push -u origin branche` | Envoyer la branche sur GitHub |
| `git pull --ff-only origin develop` | Mettre à jour sans créer de merge implicite |
| `git log --oneline --graph --all` | Visualiser l'historique et les branches |
