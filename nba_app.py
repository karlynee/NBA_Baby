# Imports de librairies
import streamlit as st
from helpers import get_bigquery_client, import_teams_all_stats_light_from_sql, import_teams_victory_defeat_from_sql
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import pandas_gbq
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Création du client BigQuery
client = get_bigquery_client()

# Importation des datasets
df_teams1 = import_teams_all_stats_light_from_sql(client)
df_teams3 = import_teams_victory_defeat_from_sql(client)

# --------------------------------------- Front

def main():
    # 1. Configurer la page
    st.set_page_config(
    page_title="NBA Baby",
    page_icon="🏀",  
    layout="wide",   # 'centered' ou 'wide'
    )
    # Title
    st.title("NBA BABY")
    st.write("Bienvenue sur la page principale de notre dashboard")

    # 2. Side bar
    st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)
    #st.sidebar.title("Teams")
    #option = st.sidebar.selectbox("Pick you team :", ["Option 1", "Option 2", "Option 3"])
    #st.write(f"Vous avez sélectionné : {option}")


    # Affichage des données dans l'interface
    st.write("Données de l'équipe :")
    st.write(df_teams1.head())




if __name__ == "__main__":
    main()