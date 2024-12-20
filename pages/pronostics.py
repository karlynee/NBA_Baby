# Imports de librairies
import streamlit as st
import sys
import os
import time

# Ajouter le répertoire parent (nba_app) au sys.path pour pouvoir importer helpers.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from helpers import (
    get_bigquery_client, 
    import_teams_all_stats_light_from_sql, 
    import_teams_victory_defeat_from_sql,
    import_players_all_stats_from_sql,
    label_encoder_teams_pred,
    load_model_with_pickle,
    predict_team1_win,
    get_team_logos
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

option_home = 'New Orleans Pelicans'
option_away = 'Phoenix Suns'

with st.container():
    st.header("Predict the Winner: Machine Learning Insights")
    st.header(" ")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
    with col2:        
        # Dropdown menu:
        option_home = st.selectbox('Pick a  Home team:', teams,
                                   index=None)
    with col3:        
        # Dropdown menu:
        option_away = st.selectbox('Pick an Away team:', teams,
                                   index=None)
    with col1:
        
        var_get_team_logos = get_team_logos(option_home)
        selected_team_home = option_home
        try:
            if selected_team_home:
                img_url_home = get_team_logos(selected_team_home)
            if img_url_home:
                st.image(img_url_home, width= 400, use_container_width=False)
            else:
                st.write(f"Photo de {selected_team_home} non disponible.")
        except:
            st.write(f'')
    with col4:
        var_get_team_logos = get_team_logos(option_away)
        selected_team_away = option_away
        try:
            if selected_team_away:
                img_url_away = get_team_logos(selected_team_away)
            if img_url_away:
                st.image(img_url_away, width= 400, use_container_width=False)
            else:
                st.write(f"Photo de {selected_team_away} non disponible.")
        except:
            st.write(f'')

with st.container():
    col1, col2, col3 = st.columns([0.5, 1, 0.5])

    # Pred
    with col2:
        try:
            dict_encoded_teams = label_encoder_teams_pred()
            model = load_model_with_pickle('pred/LR_model.pkl')
            # Replace `model` and `scaler` with your actual objects
            probability, prediction = predict_team1_win(option_home, option_away, 'pred/df_prediction_base.csv', model, dict_encoded_teams)
            progress_bar = col2.progress(0)
            for perc_completed in range(100):
                time.sleep(0.05)
                progress_bar.progress(perc_completed+1)

            progress_bar.empty()

            st.markdown("<h1 style='text-align: center;'>WINNER</h1>", unsafe_allow_html=True)
            winner_team = ''
            if probability < 0.5:
                winner = option_away
                img_url = img_url_away
                #st.image(img_url_away, width= 400, use_container_width=False)
                st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <img src="{img_url}" alt="Winner Image" width="400">
                </div>
                """,
                unsafe_allow_html=True
            )
            else:
                winner = option_home
                img_url = img_url_home
                #st.image(img_url_home, width= 400, use_container_width=False)
                st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <img src="{img_url}" alt="Winner Image" width="400">
                </div>
                """,
                unsafe_allow_html=True
            )

            # Display probability as a progress bar
            # st.write(f"Probability of {option_away} as visitor team winning: {probability:.2f} over {option_home} as home team")

            # Optionally, display the exact probability as a label
       
            progress = round(probability*100,2) 
            st.markdown(f""" <style> .progress-bar-container {{ width: 100%; background-color: #E0E0E0; border-radius: 25px; padding: 3px; margin: 20px 0; }} .progress-bar {{ width: {progress}%; /* Pourcentage de progression dynamique */ background-color: #76C7C0; height: 20px; border-radius: 20px; }} .progress-text {{ text-align: center; font-weight: bold; margin-top: -25px; /* Aligner avec la barre */ font-size: 18px; color: #555; }} </style> <div class="progress-bar-container"> <div class="progress-bar"></div> </div> <div class="progress-text">{progress}%</div> """, unsafe_allow_html=True)       
            st.write(f"Home Team win probability: {progress}%")

        except:
            st.write('')

st.header(" ")
st.header(" ")
st.header(" ")
st.header(" ")
st.header(" ")
st.header(" ")

with st.expander('How does the magic happen?✨'):
    with st.container():
        st.header("How does it work?")
        st.write("Machine learning trains algorithms to find patterns in data and make predictions. The algorithm learns from input data, then applies this knowledge to new data to predict outcomes. It improves as it processes more data.")
        st.write('The metrics used for our machine learning model are the following : 2-Point Field Goals, 2-Point Field Goal Percentage, 2-Point Field Goal Attempts, 3-Point Field Goals, 3-Point Field Goal Percentage, 3-Point Field Goal Attempts, Assists, Blocks, Defensive Rebounds, Field Goals, Field Goal Percentage, Field Goal Attempts, Free Throws, Free Throw Percentage, Free Throw Attempts, Games, Minutes Played, Offensive Rebounds, Personal Fouls, Points, Steals, Turnovers, and Total Rebounds.')
