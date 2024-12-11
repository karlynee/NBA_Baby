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
        st.write('Welcome to our basketball analytics platform 🏀 — your ultimate destination for exploring the world of NBA stats, insights, and predictions 📊. This project was conceived to make basketball data accessible, engaging, and empowering for fans and enthusiasts alike. It was created as a group project by 4 Data Analytics students from Le Wagon 👩‍💻👨‍💻, completed in just two weeks in December 2024.')
        st.write('Explore comprehensive data on teams and players with detailed stats and analyses from past seasons and real-time insights from the current season. We offer interactive graphs that bring the game’s stats to life, helping you better understand team and player performance. Our prediction page lets you test your knowledge by forecasting matchups and comparing your results to our machine learning model, which delivers a 65% accuracy rate based on key metrics like Field Goal Percentage (FG%) and Assists (AST).')
        st.header("Our Data Sources") 
        st.write("To build this website and its dashboards, we sourced our data from these resources:")
        st.write("Basketball Reference for detailed player and team stats. (https://www.basketball-reference.com)")
        st.write("NBA official website for team logos and NBA updates. (https://www.nba.com/games)")
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
