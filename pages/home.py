# Imports de librairies
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import pandas_gbq
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
import sys

# Ajouter le répertoire parent (nba_app) au sys.path pour pouvoir importer helpers.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import (get_bigquery_client, import_players_advanced_mean_from_sql,
import_teams_all_stats_light_from_sql, import_players_all_stats_from_sql,
import_teams_victory_defeat_from_sql, Rank_top_player, yesterday_results,
Rank_top_teams, Rank_conference_W_E, #create_scorecard_match_yesterday
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
    st.markdown("""
            <style>
                .block-container {
                        padding-top: 1rem;
                        padding-bottom: 0rem;
                        padding-left: 5rem;
                        padding-right: 5rem;
                    }
            </style>
            """, unsafe_allow_html=True)
    st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)
    try:
        st.markdown( """ <style> /* Style for sidebar title */ [data-testid="stSidebar"] h1 { color: #ffffff; /* Change title color */ font-size: 24px; /* Change title font size */ font-weight: bold; /* Make title bold */ } /* Style for links in the sidebar */ [data-testid="stSidebar"] .css-q8sbsg { color: #ffffff !important; /* Link text color */ font-size: 18px; /* Adjust font size */ font-weight: bold; /* Make links bold */ } /* Hover effect for links */ [data-testid="stSidebar"] .css-q8sbsg:hover { color: #E76F51 !important; /* Change color on hover */ text-decoration: underline; /* Underline on hover */ } </style> """, unsafe_allow_html=True, )    # Sidebar navigation
        st.markdown(
            """
            <style>
            body {
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.sidebar.title('🏀 NBAddicts 🏀')
        st.sidebar.page_link('pages/home.py', label='🏠 Home')
        st.sidebar.page_link('pages/players.py', label='⛹️ Players')
        st.sidebar.page_link('pages/teams.py', label='🤝 Teams')
        st.sidebar.page_link('pages/pronostics.py', label='🔮 Future Games Predictions')
        st.sidebar.page_link('pages/about_us.py', label='ℹ️ About us')


    except:
        'Page not available'

    # Title
    st.title("Welcome to the NBAddicts dashboard")
    st.write("Where statistics and NBA make a great match 📈 ❤️")
    st.title(" ")


    # --------------------- Scraping info de la veille

    # yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    # matches = yesterday_results(yesterday)

    # if matches:
    #     for match in matches:
    #         team1_name, team1_score, team2_name, team2_score = match
    #         st.write(f"{team1_name} {team1_score} vs {team2_name} {team2_score}")
    # else:
    #     st.write("No matches found for this date.")


    # --------------------- Carroussel
    st.header("Latest games")
    matches = ['Results:', 'Detroit 120 – Boston 130', 'Indiana 90 – Brooklyn 99', 'Minnesota 108 - LA Clippers 80', 'LA Lakers 93 – Miami 134', 'Atlanta 119 – Milwaukee 104', 'Orlando 106 – Philadelphia 102']
        # Dropdown menu:
    st.selectbox('',matches)


    # 2. Seasons buttons
    #season = st.radio("Select a season:",('2022-2023', '2023-2024'))
    st.session_state.selected_season = '23-24'

    with st.container():
        st.write("")
        st.write("")

    with st.container():
        col1, col2 = st.columns([1, 10])
    with col1:
        if col1.button("2022-2023"):
            st.session_state.selected_season = '22-23'
    with col2:
        if col2.button("2023-2024"):
            st.session_state.selected_season = '23-24'

    with st.container():
        st.write("")

    # -------------------------------- Top 3 tables
    rank_top_player = Rank_top_player(df_players_all_stats,st.session_state.selected_season)
    rank_top_team = Rank_top_teams(df_cleaned_all_stats_light_final_22_23_24,st.session_state.selected_season)
    rank_conference = Rank_conference_W_E(df_cleaned_all_stats_light_final_22_23_24,st.session_state.selected_season)

    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.header(f'Top 3 players {st.session_state.selected_season}')
            st.write(rank_top_player)

        with col2:   
            st.header(f"Top 3 teams {st.session_state.selected_season}")  
            st.write(rank_top_team)

    with st.container():
        st.write("")
        st.write("")

    with st.expander('Click for Ranking by Conference'):
        with st.container():
            st.header(f"Global Ranking by Conference {st.session_state.selected_season}")  
            st.write(rank_conference)

                


if __name__ == "__main__":
    main()