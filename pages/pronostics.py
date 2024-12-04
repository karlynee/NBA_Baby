# Imports de librairies
import streamlit as st
import sys
import os

# Ajouter le répertoire parent (nba_app) au sys.path pour pouvoir importer helpers.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import (
    get_bigquery_client, 
    import_teams_all_stats_light_from_sql, 
    import_teams_victory_defeat_from_sql,
    scorecards, donutWL, shootbyteam, scorecard_rank,
    win_loss, get_team_logos, major5byteam,
    import_players_all_stats_from_sql
)

# Call du client BigQuery
client = get_bigquery_client()

# Importation des datasets
df_cleaned_all_stats_light_final_22_23_24 = import_teams_all_stats_light_from_sql(client)
df_cleaned_schedule_box_22_23_24 = import_teams_victory_defeat_from_sql(client)
df_players_all_stats = import_players_all_stats_from_sql(client)


# --------------------------------------------------- Front 
# 1. Configurer la page
st.set_page_config(
    page_title="NBAddicts",
    page_icon="🏀",  
    layout="wide",   # 'centered' ou 'wide'
    )

st.sidebar.title('🏀 NBAddicts 🏀')
st.sidebar.page_link('pages/home.py', label='🏠 Home')
st.sidebar.page_link('pages/players.py', label='⛹️ Players')
st.sidebar.page_link('pages/teams.py', label='🤝 Teams')
st.sidebar.page_link('pages/pronostics.py', label='🔮 Future Games Predictions')
st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)