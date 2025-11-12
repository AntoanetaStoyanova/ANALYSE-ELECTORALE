# Analyse Électorale — Présidentielle France 2022

Ce projet permet d'analyser les résultats des élections présidentielles françaises de 2022 (tour 1 et tour 2) par commune et département.  
Les données proviennent de [DataGouv](https://www.data.gouv.fr/fr/](https://www.data.gouv.fr/) et sont transformées pour être visualisées facilement via une application **Streamlit**.


##  Fonctionnalités

- **ETL des données** :
  - Chargement des fichiers Excel des résultats par commune pour les deux tours.
  - Transformation des données en format "long" par candidat.
  - Harmonisation des numéros de candidats entre tour 1 et tour 2.
  - Export en **Parquet** pour un stockage et une lecture rapide.

- **Visualisation interactive** 
  - Indicateurs globaux : inscrits, votants, abstentions, blancs, nuls, exprimés.
  - Comparaison des tours à l’échelle nationale.
  - Analyse par département : cartes choroplèthes et métriques des départements remarquables.
  - Résultats détaillés par candidat et par département.
  - Carte des voix par candidat pour le 2ᵉ tour.

## ⚙️ Installation

1. **Cloner le projet** 
```bash
git clone https://github.com/AntoanetaStoyanova/ANALYSE-ELECTORALE.git
cd OpenData
```

2. **Créer un environnement Python** 
```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```
3. **Installer les dépendances** 
```bash
pip install -r requirements.txt
```

## Notes techniques

Python 3.13
