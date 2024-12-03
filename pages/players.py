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
    get_bigquery_client, 
    import_players_all_stats_from_sql, 
    import_players_advanced_mean_from_sql,
    jauge_players, terrain, call_players, get_player_image_url, get_player_url,
)

# Call du client BigQuery
client = get_bigquery_client()

# Importation des datasets
df_players_all_stats = import_players_all_stats_from_sql(client)
df_player_mean_22_23_24 = import_players_advanced_mean_from_sql(client)


# --------------------------------------------------- Front 
# 1. Configurer la page
st.set_page_config(
    page_title="NBA Baby",
    page_icon="🏀",  
    layout="wide",   # 'centered' ou 'wide'
    )
st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)

# 2. Team Dropdown menu
players = call_players()

option = st.selectbox('Search for a player:', players)

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


# -------------- Call Functions
player_name = 'Stephen Curry'
season = '22-23'
gauges_chart = jauge_players(player_name, season, df_players_all_stats)

st.plotly_chart(jauge_players(option, st.session_state.selected_season, df_players_all_stats))
st.plotly_chart(terrain(df_players_all_stats,option,st.session_state.selected_season))




# --------------------- Scraping images players

var_get_player_image_url = get_player_image_url(option)
var_get_player_url = get_player_url(option)
selected_player = option

# Afficher l'image du joueur sélectionné
if selected_player:
    img_url = get_player_image_url(selected_player)
    if img_url:
        st.image(img_url, use_container_height=3000 , use_container_width=3000)
    else:
        st.write(f"Photo de {selected_player} non disponible.")


