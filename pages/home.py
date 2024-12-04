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
Rank_top_teams, Rank_conference_W_E, create_scorecard_match_yesterday
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
    page_title="NBAddicts",
    page_icon="🏀",  
    layout="wide",   # 'centered' ou 'wide'
    )

    st.header('Home')
    # Sidebar navigation
    st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)

    st.sidebar.title('🏀 NBAddicts 🏀')
    st.sidebar.page_link('pages/home.py', label='🏠 Home')
    st.sidebar.page_link('pages/players.py', label='⛹️ Players')
    st.sidebar.page_link('pages/teams.py', label='🤝 Teams')
    st.sidebar.page_link('pages/pronostics.py', label='🔮 Future Games Predictions')


    # Title
    st.title("Welcome to the NBAddicts dashboard")
    st.header("Where statistics and NBA make a great match")

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


    # -------------------------------- Call Functions
    ## team_name = 'Boston Celtics'
    ## season = '22-23'

    rank_top_player = Rank_top_player(df_players_all_stats,st.session_state.selected_season)
    rank_top_team = Rank_top_teams(df_cleaned_all_stats_light_final_22_23_24,st.session_state.selected_season)
    rank_conference = Rank_conference_W_E(df_cleaned_all_stats_light_final_22_23_24,st.session_state.selected_season)

    # 3. Graphs
    #st.write("Données de l'équipe :"
    #st.write(df_cleaned_all_stats_light_final_22_23_24.head())
    st.write(rank_top_player)
    st.write(rank_top_team)
    st.write(rank_conference)
    st.write()
    

# --------------------- Scraping info de la veille
    scorecard_match_yesterday = create_scorecard_match_yesterday()
    st.write(scorecard_match_yesterday)
    # print(scorecard_match_yesterday)




if __name__ == "__main__":
    main()