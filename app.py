# -------------------------------
# IMPORTATIONS
# -------------------------------
import streamlit as st
import pandas as pd
import os
import plotly.express as px
import requests
import json


# -------------------------------
# CONFIGURATION DE LA PAGE
# -------------------------------
st.set_page_config(page_title="Analyse Électorale France", layout="wide")
st.title("Analyse Électorale — Présidentielle France")


# -------------------------------
# CHARGEMENT DES DONNÉES
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "parquets", "candidat.parquet")

@st.cache_data
def load_data(path):
    return pd.read_parquet(path)

df = load_data(FILE_PATH)


# -------------------------------
# INDICATEURS GLOBAUX
# -------------------------------
st.header("Indicateurs globaux (tous tours confondus)")

total_inscrits = df['Inscrits'].sum()
total_votants = df['Votants'].sum()
total_abst = df['Abstentions'].sum()
total_blancs = df['Blancs'].sum()
total_nuls = df['Nuls'].sum()
total_expr = df['Exprimés'].sum()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Inscrits", f"{total_inscrits:,}")
col2.metric("Votants", f"{total_votants:,}")
col3.metric("Abstentions", f"{total_abst:,}")
col4.metric("Blancs", f"{total_blancs:,}")
col5.metric("Nuls", f"{total_nuls:,}")
col6.metric("Exprimés", f"{total_expr:,}")


# -------------------------------
# COMPARAISON DES TOURS
# -------------------------------
st.header("Comparaison Tour 1 vs Tour 2")
df_tours = df.groupby('tour')[['Inscrits', 'Votants', 'Abstentions', 'Blancs', 'Nuls', 'Exprimés']].sum().reset_index()


# -------------------------------
# CHARGEMENT GEOJSON
# -------------------------------
@st.cache_data
def load_geojson_communes():
    url = "https://france-geojson.gregoiredavid.fr/repo/communes.geojson"
    return requests.get(url).json()

@st.cache_data
def load_geojson_departements():
    url = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
    return requests.get(url).json()

geojson_communes = load_geojson_communes()
geojson_departements = load_geojson_departements()


# -------------------------------
# ANALYSE PAR DÉPARTEMENT
# -------------------------------
tour = st.radio("Sélectionnez le tour :", options=sorted(df["tour"].unique()))
df_tour = df[df["tour"] == tour]

df_dep = df_tour.groupby(["Code du département", "Libellé du département"]).agg({
    "Inscrits": "sum",
    "Votants": "sum",
    "Abstentions": "sum",
    "% Abs/Ins": "mean",
    "Blancs": "sum",
    "% Blancs/Ins": "mean",
    "% Blancs/Vot": "mean"
}).reset_index()

st.subheader("Départements remarquables")

max_votants = df_dep.loc[df_dep["Votants"].idxmax()]
min_votants = df_dep.loc[df_dep["Votants"].idxmin()]
max_abst = df_dep.loc[df_dep["Abstentions"].idxmax()]
max_inscrits = df_dep.loc[df_dep["Inscrits"].idxmax()]
min_inscrits = df_dep.loc[df_dep["Inscrits"].idxmin()]

def format_number(x):
    return format(int(x), ",").replace(",", " ")

col1, col2 = st.columns(2)
with col1:
    st.metric("Plus de votants", f"{max_votants['Libellé du département']}", delta=f"{format_number(max_votants['Votants'])} votants")
    st.metric("Plus d’inscrits", f"{max_inscrits['Libellé du département']}", delta=f"{format_number(max_inscrits['Inscrits'])} inscrits")
with col2:
    st.metric("Moins de votants", f"{min_votants['Libellé du département']}", delta=f"-{format_number(min_votants['Votants'])} votants")
    st.metric("Moins d’inscrits", f"{min_inscrits['Libellé du département']}", delta=f"-{format_number(min_inscrits['Inscrits'])} inscrits")


# -------------------------------
# CARTE CHOROPLETHE DEPARTEMENTS
# -------------------------------
st.subheader(f"Carte des votants par département (Tour {tour})")

fig_map = px.choropleth_mapbox(
    df_dep,
    geojson=geojson_departements,
    locations="Code du département",
    featureidkey="properties.code",
    color="Votants",
    hover_name="Libellé du département",
    hover_data={"Votants": True, "Inscrits": True, "Abstentions": True, "% Abs/Ins": True},
    color_continuous_scale="YlGnBu",
    mapbox_style="carto-positron",
    zoom=4.3,
    center={"lat": 46.6, "lon": 2.4},
    opacity=0.85,
    title="Nombre de votants par département",
    height=600
)
st.plotly_chart(fig_map, use_container_width=True)


# -------------------------------
# ANALYSE PAR CANDIDAT TOUR 1
# -------------------------------
st.markdown("---")
st.header("Résultats du 1er tour par département")

df_tour1 = df[df["tour"] == 1]

departement_candidat = st.selectbox(
    "Choisissez un département pour voir les résultats du 1er tour :",
    sorted(df_tour1["Libellé du département"].unique())
)

df_dep_cand = df_tour1[df_tour1["Libellé du département"] == departement_candidat].copy()
df_dep_cand["Nom complet"] = df_dep_cand["Prénom"].str.strip() + " " + df_dep_cand["Nom"].str.strip()

resultats_candidats = df_dep_cand.groupby("Nom complet").agg({"Voix": "sum", "% Voix/Exp": "mean"}).sort_values("Voix", ascending=False).reset_index()

resultats_candidats_display = resultats_candidats.copy()
resultats_candidats_display["Voix"] = resultats_candidats_display["Voix"].apply(format_number)
resultats_candidats_display.rename(columns={"Nom complet": "Candidat", "% Voix/Exp": "% Voix exprimées"}, inplace=True)

st.dataframe(resultats_candidats_display)

fig_cand = px.bar(
    resultats_candidats,
    x="Nom complet",
    y="Voix",
    color="Nom complet",
    text="Voix",
    title=f"Nombre de voix par candidat — Département {departement_candidat} (Tour 1)"
)
fig_cand.update_traces(texttemplate="%{text:,}", textposition="outside")
fig_cand.update_layout(xaxis_title="Candidat", yaxis_title="Nombre de voix", height=600, showlegend=False)
st.plotly_chart(fig_cand, use_container_width=True)


# -------------------------------
# ANALYSE PAR CANDIDAT TOUR 2
# -------------------------------
st.markdown("---")
st.header("Résultats du 2ᵉ tour par département")

df_tour2 = df[df["tour"] == 2]

departement_candidat_t2 = st.selectbox(
    "Choisissez un département pour voir les résultats du 2ᵉ tour :",
    sorted(df_tour2["Libellé du département"].unique())
)

df_dep_cand_t2 = df_tour2[df_tour2["Libellé du département"] == departement_candidat_t2].copy()
df_dep_cand_t2["Nom complet"] = df_dep_cand_t2["Prénom"].str.strip() + " " + df_dep_cand_t2["Nom"].str.strip()

resultats_candidats_t2 = df_dep_cand_t2.groupby("Nom complet").agg({"Voix": "sum", "% Voix/Exp": "mean"}).sort_values("Voix", ascending=False).reset_index()

resultats_candidats_display_t2 = resultats_candidats_t2.copy()
resultats_candidats_display_t2["Voix"] = resultats_candidats_display_t2["Voix"].apply(format_number)
resultats_candidats_display_t2.rename(columns={"Nom complet": "Candidat", "% Voix/Exp": "% Voix exprimées"}, inplace=True)

st.dataframe(resultats_candidats_display_t2)

fig_cand_t2 = px.bar(
    resultats_candidats_t2,
    x="Nom complet",
    y="Voix",
    color="Nom complet",
    text="Voix",
    title=f"Nombre de voix par candidat — Département {departement_candidat_t2} (Tour 2)"
)
fig_cand_t2.update_traces(texttemplate="%{text:,}", textposition="outside")
fig_cand_t2.update_layout(xaxis_title="Candidat", yaxis_title="Nombre de voix", height=600, showlegend=False)
st.plotly_chart(fig_cand_t2, use_container_width=True)


# -------------------------------
# CARTE DES VOIX PAR CANDIDAT (TOUR 2)
# -------------------------------
st.markdown("---")
st.header("Carte des voix par candidat (2ᵉ tour)")

df_tour2["Nom complet"] = df_tour2["Prénom"].str.strip() + " " + df_tour2["Nom"].str.strip()
candidats_t2 = sorted(df_tour2["Nom complet"].unique())
candidat_t2 = st.selectbox("Choisissez un candidat du 2ᵉ tour :", candidats_t2)

df_candidat_t2 = df_tour2[df_tour2["Nom complet"] == candidat_t2]
df_cand_dep_t2 = df_candidat_t2.groupby(["Code du département", "Libellé du département"]).agg({"Voix": "sum"}).reset_index()
df_cand_dep_t2["Voix formatées"] = df_cand_dep_t2["Voix"].apply(lambda x: format(int(x), ",").replace(",", " "))

total_voix = df_cand_dep_t2["Voix"].sum()
st.metric(label=f"Total des voix pour {candidat_t2}", value=f"{total_voix:,}".replace(",", " "))

fig_map_t2 = px.choropleth_mapbox(
    df_cand_dep_t2,
    geojson=geojson_departements,
    locations="Code du département",
    featureidkey="properties.code",
    color="Voix",
    color_continuous_scale="RdYlBu_r",
    mapbox_style="carto-positron",
    zoom=4.3,
    center={"lat": 46.6, "lon": 2.4},
    opacity=0.85,
    hover_name="Libellé du département",
    hover_data={"Voix formatées": True, "Voix": False},
    title=f"Nombre de voix par département pour {candidat_t2} (2ᵉ tour)",
    height=800
)
st.plotly_chart(fig_map_t2, use_container_width=True)
