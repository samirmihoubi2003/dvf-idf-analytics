# Mesures Power BI (table : v_powerbi_transactions)

Importer la vue mart.v_powerbi_transactions avec le connecteur PostgreSQL.
Créer ces mesures via **Modélisation > Nouvelle mesure**.

```dax
Nombre de ventes = COUNTROWS('v_powerbi_transactions')
```

```dax
Volume des ventes (€) = SUM('v_powerbi_transactions'[valeur_fonciere])
```

```dax
Prix médian vente (€) = MEDIAN('v_powerbi_transactions'[valeur_fonciere])
```

```dax
Prix moyen vente (€) = AVERAGE('v_powerbi_transactions'[valeur_fonciere])
```

```dax
Prix médian m² (€) = MEDIAN('v_powerbi_transactions'[prix_m2])
```

```dax
Prix moyen m² (€) = AVERAGE('v_powerbi_transactions'[prix_m2])
```

```dax
Ventes avec prix m² = CALCULATE([Nombre de ventes], 'v_powerbi_transactions'[prix_m2_eligible] = TRUE())
```

```dax
Taux éligible prix m² = DIVIDE([Ventes avec prix m²], [Nombre de ventes])
```

**Important :** les prix au m² ne sont disponibles que pour les transactions considérées
comme non ambiguës ; Power BI ignore les BLANK dans les médianes et moyennes.
Le nombre total de ventes et le volume des ventes couvrent un ensemble plus large.

## Visuels recommandés
- 4 cartes : nombre de ventes, volume, prix médian vente et prix médian/m²
- Courbe : évolution mensuelle du nombre de ventes
- Barres : prix médian/m² par département
- Carte : nombre de ventes par commune (code INSEE + libellé)
- Segments : année, département et type de bien
- Page qualité : taux de ventes éligibles au prix au m²
