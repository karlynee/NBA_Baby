# Imports de librairies
import streamlit as st
import sys
import os
import re
import requests
from bs4 import BeautifulSoup

# Ajouter le répertoire parent (nba_app) au sys.path pour pouvoir importer helpers.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import (
    get_bigquery_client, import_players_all_stats_from_sql, 
    import_players_advanced_mean_from_sql, players_scorecards,
    jauge_players, terrain, call_players, get_player_image_url, get_player_url,
    sc_pres
)

# Call du client BigQuery
client = get_bigquery_client()

# Importation des datasets
df_players_all_stats = import_players_all_stats_from_sql(client)
df_player_mean_22_23_24 = import_players_advanced_mean_from_sql(client)


# --------------------------------------------------- Front 
# 1. Configurer la page
st.set_page_config(
    page_title="NBAddicts",
    page_icon="🏀",  
    layout="wide",   # 'centered' ou 'wide'
    )
st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)

st.sidebar.title('🏀 NBAddicts 🏀')
st.sidebar.page_link('pages/home.py', label='🏠 Home')
st.sidebar.page_link('pages/players.py', label='⛹️ Players')
st.sidebar.page_link('pages/teams.py', label='🤝 Teams')
st.sidebar.page_link('pages/pronostics.py', label='🔮 Future Games Predictions')
# st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)


# 2. Team Dropdown menu
players = call_players()

option = st.selectbox(':grey[Search for a player:]', players)

# 3. Seasons buttons
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

# --------------------- Scraping images players
# Afficher l'image du joueur sélectionné
var_get_player_image_url = get_player_image_url(option)
var_get_player_url = get_player_url(option)
selected_player = option
try:
    if selected_player:
        img_url = get_player_image_url(selected_player)
    if img_url:
        st.image(img_url, width= 400, use_container_width=False)
    else:
        st.write(f"Photo de {selected_player} non disponible.")
except:
    st.write(f'{option} did not play during the season {st.session_state.selected_season}')


# -------------- Call Functions
#try:
st.plotly_chart(sc_pres(df_players_all_stats,option, st.session_state.selected_season,'Pos'))
st.plotly_chart(sc_pres(df_players_all_stats,option, st.session_state.selected_season,'Team'))
st.plotly_chart(sc_pres(df_players_all_stats,option, st.session_state.selected_season,'PER'))
st.plotly_chart(sc_pres(df_players_all_stats,option, st.session_state.selected_season,'Age'))
                    
st.plotly_chart(jauge_players(option, st.session_state.selected_season, df_players_all_stats))
st.plotly_chart(terrain(df_players_all_stats,option,st.session_state.selected_season))
#except:
    #st.write(f'{option} did not play during the season {st.session_state.selected_season}')

st.plotly_chart(players_scorecards(df_players_all_stats, df_player_mean_22_23_24,option,st.session_state.selected_season)) #Streamlit






