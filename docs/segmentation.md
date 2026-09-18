# Journal d'évolution — Segmentation Client (M3, M4)

> Historique des décisions techniques du module segmentation.
> Ajouter les nouvelles entrées à la fin, ne jamais réécrire l'historique.

---

## 11 septembre 2026 — Problème identifié : segmentation non persistée

**Ce qui a été identifié**
`client_segmentation.py` recalcule entièrement le clustering K-Means et
les bornes de quantiles RFM (scores R/F/M) à chaque exécution, sans
sauvegarder ni le scaler, ni le modèle K-Means, ni les bornes utilisées.

**Pourquoi c'est un problème**
Contrairement au module churn (`train.py` persiste
`churn_model.joblib`/`scaler.joblib`/`feature_columns.joblib`, réutilisés
tels quels par `predict.py`), rien ici ne garantit qu'un même client
reçoive le même cluster/segment d'une exécution à l'autre si la
population de clients en entrée change. Les bornes de `pd.qcut` et les
centroïdes K-Means sont recalculés sur les données du moment — la
définition de "VIP" ou "À risque" peut donc se déplacer silencieusement
d'une exécution à l'autre, sans qu'aucun client n'ait réellement changé
de comportement.

**Décision**
Scinder le module en une étape d'entraînement (calcule et persiste
scaler + modèle K-Means + bornes de quantiles) et une étape de scoring
(recharge ces artefacts, les applique sans les recalculer) — même
principe que `train.py`/`predict.py` côté churn. Implémentation à
détailler dans une prochaine entrée, une fois validée avec le binôme
responsable du module.

---

## 11 septembre 2026 — predict_segmentation.py implémenté, validation croisée churn/segment

**Ce qui a changé / a été décidé**
Bug corrigé dans `train_segmentation.py` : `compute_quantile_edges`
calculait les bornes sur les rangs (`.rank()`) plutôt que sur les
valeurs RFM brutes, provoquant des NaN au predict (bornes appliquées à
une échelle différente de celle sur laquelle elles avaient été
calculées). Corrigé pour calculer les bornes directement sur les
valeurs, avec `duplicates="drop"` pour gérer les cas où trop de valeurs
identiques (surtout Frequency, entière) empêchent 5 tranches distinctes.

`predict_segmentation.py` implémenté : recharge scaler/kmeans/
log_columns/quantile_edges, applique sans réentraîner (transform/predict
only, pd.cut avec bornes fixes au lieu de pd.qcut).

**Résultat**
Répartition très déséquilibrée : Perdus 36.5%, Occasionnels 25.7%, VIP
24.6%, Fidèles 11.8%, À risque 1.3%, Nouveaux 0.1%. Client 633 (seul
"Nouveaux") vérifié manuellement — profil cohérent avec la règle de
label_from_rfm, pas un bug.

Taux de churn par segment très cohérent avec les noms (Perdus 100%,
À risque 77%, VIP/Fidèles 0%) — confirme que le pipeline capture un
vrai signal RFM plutôt qu'un artefact.

**Limite à noter pour M9**
Cette cohérence quasi parfaite n'est pas une preuve de qualité
généralisable : RFM et Churn dérivent tous les deux du même
`_Behavior` déterministe dans generate_data.py (voir docs/churn.md).
La segmentation retrouve le même signal que le modèle churn plutôt que
d'apporter une validation indépendante.

---
