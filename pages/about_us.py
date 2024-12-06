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
from helpers import (get_bigquery_client)

# Création du client BigQuery
client = get_bigquery_client()

# --------------------------------------- Front

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
    st.sidebar.title('🏀 NBAddicts 🏀')
    st.sidebar.page_link('pages/home.py', label='🏠 Home')
    st.sidebar.page_link('pages/players.py', label='⛹️ Players')
    st.sidebar.page_link('pages/teams.py', label='🤝 Teams')
    st.sidebar.page_link('pages/pronostics.py', label='🔮 Future Games Predictions')
    st.sidebar.page_link('pages/about_us.py', label='🧑 About us')


except:
    'Page not available'

with st.container():
    col1, col2,col3 = st.columns([2,1,1], vertical_alignment= 'center')
    
    with col1 : 
        st.header("About Us")
        st.write('The metrics used for our machine learning model are the following : 2-Point Field Goals, 2-Point Field Goal Percentage, 2-Point Field Goal Attempts, 3-Point Field Goals, 3-Point Field Goal Percentage, 3-Point Field Goal Attempts, Assists, Blocks, Defensive Rebounds, Field Goals, Field Goal Percentage, Field Goal Attempts, Free Throws, Free Throw Percentage, Free Throw Attempts, Games, Minutes Played, Offensive Rebounds, Personal Fouls, Points, Steals, Turnovers, and Total Rebounds.')
        st.header("Our Data Sources") 
        st.write("To build this website and its dashboards, we sourced our data from these resources:")
        st.write("Basketball Reference for detailed player and team stats. (https://www.basketball-reference.com)")
        st.write("NBA official website for team logos and NBA updates. (https://www.nba.com/games)")
        st.write("YouTube for our PowerPoint presentation. (https://www.youtube.com/watch?v=fA20AqLuDjc)")
        st.write("Whether you’re here to explore stats, challenge yourself, or deepen your love for basketball, this is the place for you.")
        st.header("Authors")
        url1='https://www.linkedin.com/in/thomas-quatreboeufs-72199871/'
        url2='https://www.linkedin.com/in/jeremyboyer/'
        url3='https://www.linkedin.com/in/karlyne-malonga-2ba23b107/'
        url4='https://www.linkedin.com/in/catalina-bucovineanu-47b74922b/'
        st.write("Jeremy Boyer [LinkedIn](%s)"% url2)
        st.write("Thomas Quatreboeufs [LinkedIn](%s)"% url1)
        st.write("Karlyne Malonga [LinkedIn](%s)"% url3)
        st.write("Catalina Bucovineanu [LinkedIn](%s)"% url4)

    with col3 : 
        st.header(" ")
        st.header(" ")
        st.header(" ")
        st.header(" ")
        st.header(" ")
        st.header(" ")
        st.header(" ")
        st.header(" ")
        st.image('images/Nba baby QR Code.png')
