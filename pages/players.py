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
    jauge_players, terrain, call_players, get_player_image_url, get_player_url
    ,sc_pres2
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
try: 
    st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)
    st.markdown( """ <style> /* Style for sidebar title */ [data-testid="stSidebar"] h1 { color: #ffffff; /* Change title color */ font-size: 24px; /* Change title font size */ font-weight: bold; /* Make title bold */ } /* Style for links in the sidebar */ [data-testid="stSidebar"] .css-q8sbsg { color: #ffffff !important; /* Link text color */ font-size: 18px; /* Adjust font size */ font-weight: bold; /* Make links bold */ } /* Hover effect for links */ [data-testid="stSidebar"] .css-q8sbsg:hover { color: #E76F51 !important; /* Change color on hover */ text-decoration: underline; /* Underline on hover */ } </style> """, unsafe_allow_html=True, )    # Sidebar navigation
    st.sidebar.title('🏀 NBAddicts 🏀')
    st.sidebar.page_link('pages/home.py', label='🏠 Home')
    st.sidebar.page_link('pages/players.py', label='⛹️ Players')
    st.sidebar.page_link('pages/teams.py', label='🤝 Teams')
    st.sidebar.page_link('pages/pronostics.py', label='🔮 Future Games Predictions')
    st.sidebar.page_link('pages/about_us.py', label='ℹ️ About us')

except:
    'Page not available'

with st.container():
    col1, col2 = st.columns([1, 4])
    with col2:
        players = call_players()
        option = st.selectbox(':grey[Search for a player:]', players)
        st.session_state.selected_season = '23-24'
        with st.container():
            col3, col4, col5 = st.columns([1, 1, 6], vertical_alignment= 'center')
            with col3:
                if col3.button("2022-2023"):
                    st.session_state.selected_season = '22-23'
            with col4:
                if col4.button("2023-2024"):
                    st.session_state.selected_season = '23-24'
            with col5:
                ""    

# -------------- Player main info
        with st.container():
            col3, col4, col5, col6 = st.columns([2, 1, 1, 1])
            with col3: 
                metric_column_team,player_metric_team = sc_pres2(df_players_all_stats, option,st.session_state.selected_season, metric_column='Team')
                st.metric(label = metric_column_team, value = player_metric_team)

            with col4: 
                metric_column_age,player_metric_age = sc_pres2(df_players_all_stats, option,st.session_state.selected_season, metric_column='Age')
                st.metric(label = metric_column_age, value = player_metric_age)

            with col5: 
                metric_column_pos,player_metric_pos = sc_pres2(df_players_all_stats, option,st.session_state.selected_season, metric_column='Pos')
                st.metric(label = metric_column_pos, value = player_metric_pos)

            with col6: 
                metric_column_per,player_metric_per = sc_pres2(df_players_all_stats, option,st.session_state.selected_season, metric_column='PER')
                st.metric(label = metric_column_per, value = player_metric_per, delta=f"avg league: 15", help="Player Efficiency Rating - A measure of per-minute production")


    # with col1:
        
        # --------------------- Scraping images players
        # Afficher l'image du joueur sélectionné
        # var_get_player_image_url = get_player_image_url(option)
        # var_get_player_url = get_player_url(option)
        # selected_player = option
        # try:
        #     if selected_player:
        #         img_url = get_player_image_url(selected_player)
        #     if img_url:
        #         st.image(img_url, width= 160, use_container_width=False)
        #     else:
        #         st.write(f"Photo de {selected_player} non disponible.")
        # except:
        #     st.write(f'{option} did not play during the season {st.session_state.selected_season}')
st.write('')
st.write('')
with st.container():
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1,1, 1], vertical_alignment= 'center')
    
    with col1 : 
        metric_column_pts, player_metric_pts, mean_metric_pts = players_scorecards(df_players_all_stats, df_player_mean_22_23_24,option,st.session_state.selected_season,metric_column='PTS')
        st.metric(label = metric_column_pts, value = player_metric_pts, delta=f"avg league: {mean_metric_pts}", help="Number of points per match")

    with col2 : 
        metric_column_TRB, player_metric_TRB, mean_metric_TRB = players_scorecards(df_players_all_stats, df_player_mean_22_23_24,option,st.session_state.selected_season,metric_column='TRB')
        st.metric(label = metric_column_TRB, value = player_metric_TRB, delta=f"avg league: {mean_metric_TRB}", help="Number of rebounds per match")

    with col3 : 
        metric_column_AST, player_metric_AST, mean_metric_AST = players_scorecards(df_players_all_stats, df_player_mean_22_23_24,option,st.session_state.selected_season,metric_column='AST')
        st.metric(label = metric_column_AST, value = player_metric_AST, delta=f"avg league: {mean_metric_AST}", help="Number of assists per match")
    
    with col4 : 
        metric_column_STL, player_metric_STL, mean_metric_STL = players_scorecards(df_players_all_stats, df_player_mean_22_23_24,option,st.session_state.selected_season,metric_column='STL')
        st.metric(label = metric_column_STL, value = player_metric_STL, delta=f"avg league: {mean_metric_STL}", help="Number of steals per match")
    
    with col5 : 
        metric_column_BLK, player_metric_BLK, mean_metric_BLK = players_scorecards(df_players_all_stats, df_player_mean_22_23_24,option,st.session_state.selected_season,metric_column='BLK')
        st.metric(label = metric_column_BLK, value = player_metric_BLK, delta=f"avg league: {mean_metric_BLK}", help="Number of blocks per match")
    
    with col6 : 
        metric_column_MP, player_metric_MP, mean_metric_MP = players_scorecards(df_players_all_stats, df_player_mean_22_23_24,option,st.session_state.selected_season,metric_column='MP')
        st.metric(label = metric_column_MP, value = player_metric_MP, delta=f"avg league: {mean_metric_MP}", help="Number of minutes played per match")

# -------------- Call Functions
# -------------- Player main info
with st.container():
    col1, col2 = st.columns([1,1])
    with col1: 
        st.plotly_chart(jauge_players(option, st.session_state.selected_season, df_players_all_stats))
    with col2: 
        st.plotly_chart(terrain(df_players_all_stats,option,st.session_state.selected_season))

        #st.write(f'{option} did not play during the season {st.session_state.selected_season}')
# with st.container():
    # st.plotly_chart(players_scorecards(df_players_all_stats, df_player_mean_22_23_24,option,st.session_state.selected_season)) #Streamlit
