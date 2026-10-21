# Méthodologie DVF

## Périmètre
- Île-de-France : 75, 77, 78, 91, 92, 93, 94, 95.
- Millésimes complets par défaut : 2024 et 2025, chargement sur demande.
- Source : DVF géolocalisées Etalab, fichiers CSV.GZ par département.
- Nature mutation retenue : `Vente`. Les `Echange`, VEFA, etc. sont exclus.

## Pourquoi une vente n'est pas une ligne DVF
Une mutation peut comporter plusieurs locaux, lots, parcelles ou dépendances.
La valeur foncière est souvent répétée sur toutes ces lignes. Le grain cible est
le quadruplet `(source_year, source_department, id_mutation, numero_disposition)`.
On rejette des mutations dont dates, communes ou valeurs foncières divergent
au sein du même groupe. Ce n'est PAS une mesure par ligne de bien.

## Prix au m² (méthode volontairement conservatrice)
Pour calculer `valeur_fonciere / surface_bati`, on exige exactement **une** ligne
bâtie de type Maison ou Appartement avec surface positive, sans ligne de local
non résidentiel. Les lignes `Dépendance` peuvent accompagner la mutation.
Plusieurs lignes représentant le même local dans plusieurs parcelles peuvent
écarter une vente valide : on préfère une couverture moindre à un ratio faux.
Deux appartements vendus ensemble ne reçoivent PAS de prix au m² individuel.
Les mutations sont malgré tout retenues dans le nombre de ventes/volume.
Le prix d'une vente incluant dépendance ne représente pas nécessairement
le prix intrinsèque de la seule surface habitable : prudence à l'interprétation.

## Reproductibilité et mise à jour
Les fichiers source sont archivés dans data/raw (hors Git). Leur SHA-256 est
journalisé dans `mart.etl_runs`. Sans --force-download, on réutilise le cache ;
avec --force-download, on récupère la version la plus récente disponible.
Il faut enregistrer la date d'extraction car les millésimes DVF peuvent être
révisés par l'administration.
Les chargements sont atomiques par département-année : recharger le même fichier
remplace toutes les ventes du lot (sans doubler les transactions).

## Limites
- Source brute : données des actes fiscaux, non exhaustive à tout instant.
- Aucune estimation des prix actuels : on représente les ventes historiques.
- Aucune réidentification, indexation publique d'adresses individuelles,
  ou partage public des informations à granularité sensible.
- Certaines ventes complexes n'ont pas de prix/m² fiable.
