# Imports de librairies
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import pandas_gbq
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Ajouter le répertoire parent (nba_app) au sys.path pour pouvoir importer helpers.py
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import (get_bigquery_client, import_players_advanced_mean_from_sql,
import_teams_all_stats_light_from_sql, import_players_all_stats_from_sql,
import_teams_victory_defeat_from_sql, Rank_top_player,
Rank_top_teams, Rank_conference_W_E
)

# Création du client BigQuery
client = get_bigquery_client()

# -------------------------------- Importation des datasets
df_cleaned_all_stats_light_final_22_23_24 = import_teams_all_stats_light_from_sql(client)
df_cleaned_schedule_box_22_23_24 = import_teams_victory_defeat_from_sql(client)
df_players_all_stats = import_players_all_stats_from_sql(client)
df_player_mean_22_23_24 = import_players_advanced_mean_from_sql(client)

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

    # 2. Seasons buttons
    #season = st.radio("Select a season:",('2022-2023', '2023-2024'))
    st.session_state.selected_season = '23-24'

    with st.container():
        col1, col2 = st.columns([1, 10])
    with col1:
        if col1.button("2022-2023"):
            st.session_state.selected_season = '22-23'
    with col2:
        if col2.button("2023-2024"):
            st.session_state.selected_season = '23-24'

    # 2. Side bar
    st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)
    #st.sidebar.title("Teams")
    #option = st.sidebar.selectbox("Pick you team :", ["Option 1", "Option 2", "Option 3"])
    #st.write(f"Vous avez sélectionné : {option}")

    # -------------------------------- Call Functions
    ## team_name = 'Boston Celtics'
    ## season = '22-23'

    rank_top_player = Rank_top_player(df_players_all_stats,st.session_state.selected_season)
    rank_top_team = Rank_top_teams(df_cleaned_all_stats_light_final_22_23_24,st.session_state.selected_season)
    rank_conference = Rank_conference_W_E(df_cleaned_all_stats_light_final_22_23_24,st.session_state.selected_season)

    # 3. Graphs
    #st.write("Données de l'équipe :"
    #st.write(df_cleaned_all_stats_light_final_22_23_24.head())
    st.plotly_chart(rank_top_player)
    st.plotly_chart(rank_top_team)
    st.plotly_chart(rank_conference)
    




if __name__ == "__main__":
    main()