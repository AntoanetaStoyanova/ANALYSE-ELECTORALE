import pandas as pd
import os

# ---- 1️⃣ Définir les colonnes ----
commune_col = [
    'Code du département', 'Code de la commune', 'Libellé du département', 'Libellé de la commune',
    'Etat saisie', 'Inscrits', 'Abstentions',
    '% Abs/Ins', 'Votants', '% Vot/Ins', 'Blancs', '% Blancs/Ins', '% Blancs/Vot', 'Nuls',
    '% Nuls/Ins', '% Nuls/Vot', 'Exprimés', '% Exp/Ins', '% Exp/Vot'
]

candidat1_cols = ['N°Panneau', 'Sexe', 'Nom', 'Prénom', 'Voix', '% Voix/Ins', '% Voix/Exp']
cols_per_candidat = 7

# ---- 2️⃣ Fonction de transformation ----
def process_tour(df_tour, tour_number, start_col, num_cols):
    # Colonnes des autres candidats
    candidats_cols = []
    for i in range(start_col, num_cols + 1, cols_per_candidat):
        candidats_cols.append([f'Unnamed: {j}' for j in range(i, i + cols_per_candidat)])
    
    dfs = []
    
    # Premier candidat
    df1 = df_tour[commune_col + candidat1_cols].copy()
    df1['candidat'] = 1
    df1['tour'] = tour_number
    df1.columns = commune_col + candidat1_cols + ['candidat', 'tour']
    dfs.append(df1)
    
    # Autres candidats
    for idx, cols in enumerate(candidats_cols, start=2):
        df_c = df_tour[commune_col + cols].copy()
        df_c['candidat'] = idx
        df_c['tour'] = tour_number
        df_c.columns = commune_col + candidat1_cols + ['candidat', 'tour']
        dfs.append(df_c)
    
    return pd.concat(dfs, ignore_index=True)
# ---- :three: Orchestration du pipeline ----
def main():
    # Dossier des fichiers source
    data_dir = "data"
    parquet_dir = "parquets"
    os.makedirs(parquet_dir, exist_ok=True)
    
    # Liste des tours à traiter
    tours = [
        ("resultats-par-niveau-subcom-t1-france-entiere.xlsx", 1, 26, 102),
        ("resultats-par-niveau-subcom-t2-france-entiere.xlsx", 2, 26, 32)
    ]
    
    df_list = []
    
    for fichier, tour_number, start_col, num_cols in tours:
        print(f"Traitement de {fichier}...")
        df_tour = pd.read_excel(os.path.join(data_dir, fichier))
        df_long = process_tour(df_tour, tour_number, start_col, num_cols)
        df_list.append(df_long)
    
    # Fusionner tous les tours
    df_long_total = pd.concat(df_list, ignore_index=True)
    
    # Attribuer les numéros de candidats du tour 1 au tour 2
    df_long_total_tour2 = df_long_total[df_long_total['tour'] == 2]
    df_long_total_tour1 = df_long_total[df_long_total['tour'] == 1]
    
    df_long_total_tour2 = df_long_total_tour2.merge(
        df_long_total_tour1[['Nom', 'Prénom', 'candidat']].drop_duplicates(),
        on=['Nom', 'Prénom'],
        how='left',
        suffixes=('', '_tour1')
    )
    df_long_total_tour2['candidat'] = df_long_total_tour2['candidat_tour1']
    df_long_total_tour2.drop(columns=['candidat_tour1'], inplace=True)
    
    # Remplacer les lignes tour 2 dans le total
    df_long_total = pd.concat([df_long_total_tour1, df_long_total_tour2], ignore_index=True)
    
    # Forcer les colonnes object en string pour Parquet
    for col in df_long_total.select_dtypes(include=['object']).columns:
        df_long_total[col] = df_long_total[col].astype(str)
    
    # Sauvegarde Parquet
    output_path = os.path.join(parquet_dir, "candidat.parquet")
    df_long_total.to_parquet(output_path, index=False, engine='pyarrow')
    
    print(f"Pipeline terminé. Fichier sauvegardé : {output_path}")

if __name__ == "__main__":
    main()