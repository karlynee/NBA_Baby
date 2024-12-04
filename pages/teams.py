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
    scorecards, donutWL, shootbyteam, scorecard_rank,
    win_loss, get_team_logos, major5byteam,
    import_players_all_stats_from_sql
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
st.sidebar.title('🏀 NBAddicts 🏀')
st.sidebar.page_link('pages/home.py', label='🏠 Home')
st.sidebar.page_link('pages/players.py', label='⛹️ Players')
st.sidebar.page_link('pages/teams.py', label='🤝 Teams')
st.sidebar.page_link('pages/pronostics.py', label='🔮 Future Games Predictions')
st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)

with st.container():
    col1, col2 = st.columns([1, 4])
    with col2:
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
        # default_team = "San Antonio Spurs"
        # Dropdown menu:
        option = st.selectbox('Pick a team:', teams)
        st.session_state.selected_season = '23-24'
        st.write(option)
        # 3. Seasons buttons
        #season = st.radio("Select a season:",('2022-2023', '2023-2024'))
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
        fig_win_loss = win_loss(df_cleaned_schedule_box_22_23_24,option,st.session_state.selected_season)
        st.plotly_chart(fig_win_loss)

    with col1:
    # ---------------------- Teams Logos
        var_get_team_logos = get_team_logos(option)
        selected_team = option
        try:
            if selected_team:
                img_url = get_team_logos(selected_team)
            if img_url:
                st.image(img_url, width= 400, use_container_width=False)
            else:
                st.write(f"Photo de {selected_team} non disponible.")
        except:
            st.write(f'{option} did not play during the season {st.session_state.selected_season}')

        scorecard_rank_by_conference = scorecard_rank(df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season)
        st.write(scorecard_rank_by_conference)

# -------------- Call Functions
## team_name = 'Boston Celtics'
## season = '22-23'
scorecard_fig2P = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='_2P_',rank_column='rank_2P_')
scorecard_fig3P = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='_3P_',rank_column='rank_3P_')
scorecard_figFT = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='FT_',rank_column='rank_FT_')
scorecard_figAST = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='AST',rank_column='rank_AST')
scorecard_figTRB = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='TRB',rank_column='rank_TRB')
scorecard_figPace = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='Pace',rank_column='rank_Pace')
scorecard_figORtg = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='ORtg',rank_column='rank_ORtg')
scorecard_figDRtg = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='DRtg',rank_column='rank_DRtg')
shootbyteam_fig = shootbyteam (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season)
major5byteam_fig = major5byteam (df_players_all_stats,option,st.session_state.selected_season)

donutWL_fig = donutWL (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season)
st.plotly_chart(donutWL_fig)
print(type(scorecard_fig2P))
# ----------- Logo & stats
# 3. Win Loss chart
with st.container():
    col1, col2 = st.columns([1, 3])

    with col1:
        st.write(scorecard_fig3P)
        st.write(scorecard_figFT)
        st.write(scorecard_figAST)
        st.write(scorecard_figTRB)

    with col2:
        # st.title("Team Name")
        # st.write("premier graph ici")
        st.image("https://cdn.nba.com/logos/nba/1610612759/primary/L/logo.svg")
        st.write(scorecard_fig2P)
        st.write(scorecard_figPace)
        st.write(scorecard_figORtg)
        st.write(scorecard_figDRtg)
        st.plotly_chart(shootbyteam_fig)
        st.write(major5byteam_fig)

