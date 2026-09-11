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
