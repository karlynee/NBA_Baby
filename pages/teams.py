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
    teams_score_card
)

# Call du client BigQuery
client = get_bigquery_client()

# Importation des datasets
df_teams1 = import_teams_all_stats_light_from_sql(client)
df_teams2 = import_teams_victory_defeat_from_sql(client)

# --------------------------------------------------- Front 
# 1. Configurer la page
st.set_page_config(
    page_title="NBA Baby",
    page_icon="🏀",  
    layout="wide",   # 'centered' ou 'wide'
    )
st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)

# 2. Team Dropdown menu
teams = ['Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets',
         'Charlotte Hornets', 'Chicago Bulls', 'Cleveland Cavaliers', 
         'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons', 
         'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers', 
         'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 
         'Miami Heat', 'Milwaukee Bucks', 'Minnesota Timberwolves', 
         'New Orleans Pelicans', 'New York Knicks', 'Oklahoma City Thunder', 
         'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns', 'Portland Trail Blazers', 
         'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz', 
         'Washington Wizards']
default_team = "San Antonio Spurs"

option = st.selectbox('Pick a team:', teams)
# 3. Seasons buttons
#season = st.radio("Select a season:",('2022-2023', '2023-2024'))
with st.container():
    col1, col2 = st.columns([1, 10])
    with col1:
        if col1.button("2022-2023"):
            st.session_state.selected_season = '2022-2023'
    with col2:
        if col2.button("2023-2024"):
            st.session_state.selected_season = '2023-2024'


# ----------- Logo & stats
with st.container():
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image("https://cdn.nba.com/logos/nba/1610612737/global/L/logo.svg", use_container_width=True)

    with col2:
        # st.title("Team Name")
        # st.write("premier graph ici")
        st.image("https://cdn.nba.com/logos/nba/1610612759/primary/L/logo.svg")
        teams_score_card(df_teams1, "3P%")

# Afficher un aperçu du dataset
st.dataframe(df_teams1.head())
