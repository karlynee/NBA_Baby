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
    st.markdown( """ <style> /* Style for sidebar title */ [data-testid="stSidebar"] h1 { color: #ffffff; /* Change title color */ font-size: 24px; /* Change title font size */ font-weight: bold; /* Make title bold */ } /* Style for links in the sidebar */ [data-testid="stSidebar"] .css-q8sbsg { color: #ffffff !important; /* Link text color */ font-size: 18px; /* Adjust font size */ font-weight: bold; /* Make links bold */ } /* Hover effect for links */ [data-testid="stSidebar"] .css-q8sbsg:hover { color: #E76F51 !important; /* Change color on hover */ text-decoration: underline; /* Underline on hover */ } </style> """, unsafe_allow_html=True, )    # Sidebar navigation
    st.markdown(
        """
        <style>
        body {
        background-color: #1F4186;
        color: white; 
        }
        .white-text {
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

with st.container():
    col1, col2 = st.columns([1,1], vertical_alignment= 'center')
    
    with col1 : 
        st.header("About Us")
        st.write("Welcome to our basketball analytics platform—your ultimate destination for exploring the world of NBA stats, insights, and predictions. This project was conceived to make basketball data accessible, engaging, and empowering for fans and enthusiasts alike.")
        st.write("Here, you will find Comprehensive Data on Teams and Players")
        st.write("Our aim is to dive into detailed statistics and analyses from past seasons (currently up to 2022) and to display information over the current season through scorecards and graphical insights, from player performance to team trends.")
        st.write("This is why we’ve designed engaging and interactive graphs that bring the game’s stats to life, helping you understand and appreciate basketball on a deeper level.")
        st.write("Finally, we wanted to add a more personal touch by a prognostic page. There you can test your knowledge and challenge yourself by predicting the outcomes of team matchups that can be compared to our analytics made through machine learning. Our prediction page is powered by a custom-built model designed to deliver insights with a 65% reliability rate. By analyzing critical metrics such as Field Goal Percentage (FG%), Assists (AST), and other advanced statistics, we aim to provide you some leads for further predictions of basketball matchups.")
        st.header("Our Data Sources") 
        st.write("To build this website and its dashboards, we sourced our data from these resources:")
        st.write("Basketball Reference for detailed player and team stats. (https://www.basketball-reference.com)")
        st.write("NBA official website for team logos and NBA updates. (https://www.nba.com/games)")
        st.write("YouTube for our PowerPoint presentation. (https://www.youtube.com/watch?v=fA20AqLuDjc)")
        st.write("Whether you’re here to explore stats, challenge yourself, or deepen your love for basketball, this is the place for you.")
        st.header("Authors") 
        st.write("Jeremy Boyer")
        st.write("Thomas Quatreboeufs")
        st.write("Karlyne Malonga Linkedin")
        st.write("")

    with col2 : 
        st.write(" ")
