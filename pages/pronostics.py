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
    st.markdown( """ <style> /* Style for sidebar title */ [data-testid="stSidebar"] h1 { color: #ffffff; /* Change title color */ font-size: 24px; /* Change title font size */ font-weight: bold; /* Make title bold */ } /* Style for links in the sidebar */ [data-testid="stSidebar"] .css-q8sbsg { color: #ffffff !important; /* Link text color */ font-size: 18px; /* Adjust font size */ font-weight: bold; /* Make links bold */ } /* Hover effect for links */ [data-testid="stSidebar"] .css-q8sbsg:hover { color: #E76F51 !important; /* Change color on hover */ text-decoration: underline; /* Underline on hover */ } </style> """, unsafe_allow_html=True, )    # Sidebar navigation
    st.sidebar.title('🏀 NBAddicts 🏀')
    st.sidebar.page_link('pages/home.py', label='🏠 Home')
    st.sidebar.page_link('pages/players.py', label='⛹️ Players')
    st.sidebar.page_link('pages/teams.py', label='🤝 Teams')
    st.sidebar.page_link('pages/pronostics.py', label='🔮 Future Games Predictions')
    st.sidebar.page_link('pages/about_us.py', label='ℹ️ About us')

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
            st.write(f'Select a Home Team')
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
            st.write(f'Select an Away Team')

with st.container():
    col1, col2, col3 = st.columns([0.5, 1, 0.5])

    # Pred
    with col2:
        try:
            dict_encoded_teams = label_encoder_teams_pred()
            model = load_model_with_pickle('pred/LR_model.pkl')
            # Replace `model` and `scaler` with your actual objects
            probability, prediction = predict_team1_win(option_home, option_away, 'pred/df_prediction_base.csv', model, dict_encoded_teams)
            st.markdown('# WINNER')
            winner_team = ''
            if probability < 0.5:
                winner = option_away
                st.image(img_url_away, width= 400, use_container_width=False)

            else:
                winner = option_home
                st.image(img_url_home, width= 400, use_container_width=False)
        
            st.write(f"Probability of {option_home} as visitor team winning: {probability:.2f} over {option_away} as home team")
        except:
            st.write('')
