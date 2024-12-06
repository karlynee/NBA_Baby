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
    scorecards, donutWL, shootbyteam, scorecard_rank,
    win_loss, get_team_logos,get_player_image_url, get_player_url,
    import_players_all_stats_from_sql, scorecard_conference,major5byteam2
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
    
   # Sidebar navigation
st.sidebar.image("https://cdn.nba.com/logos/leagues/logo-nba.svg", use_container_width=True)
try:
    st.markdown( """ <style> /* Style for sidebar title */ [data-testid="stSidebar"] h1 { color: #ffffff; /* Change title color */ font-size: 24px; /* Change title font size */ font-weight: bold; /* Make title bold */ } /* Style for links in the sidebar */ [data-testid="stPageLink-NavLink"] .css-q8sbsg { color: #ffffff !important; /* Link text color */ font-size: 18px; /* Adjust font size */ font-weight: bold; /* Make links bold */ } /* Hover effect for links */ [data-testid="stSidebar"] .css-q8sbsg:hover { color: #E76F51 !important; /* Change color on hover */ text-decoration: underline; /* Underline on hover */ } </style> """, unsafe_allow_html=True, )    # Sidebar navigation
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
        
        # Dropdown menu:
        option = st.selectbox('Pick a team:', teams)
        st.session_state.selected_season = '23-24'
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
                st.image(img_url, width= 400, use_container_width=True)
            else:
                st.write(f"Photo de {selected_team} non disponible.")
        except:
            st.write(f'{option} did not play during the season {st.session_state.selected_season}')

        #scorecard_rank(df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season)
        # --------------------------------------------------------------Rank by conference
        st.metric(label = 'Conference', value = f'{scorecard_conference(df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season)}', delta=None)
        st.metric(label = 'Rank', value = f'{scorecard_rank(df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season)}/15', delta=None)


# -------------- Scorecards
with st.container():
    col6, col7, col8, col9, col10, col11, col12, col13 = st.columns([1, 1, 1, 1,1, 1,1, 1,], vertical_alignment= 'center')
    
    with col6 : 
        metric3p, team_3p, team_rank_3p = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='_3P_',rank_column='rank_3P_')
        st.metric(label = metric3p, value = team_3p, delta=f"Rank {team_rank_3p}/30", help="3 points field goals %")

    with col7 : 
        metric2p, team_2p, team_rank_2p = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='_2P_',rank_column='rank_2P_')
        st.metric(label = metric2p, value = team_2p, delta=f"Rank {team_rank_2p}/30", help="2 points field goals %")

    with col8 : 
        metricft, team_ft, team_rank_ft = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='FT_',rank_column='rank_FT_')
        st.metric(label = metricft, value = team_ft, delta=f"Rank {team_rank_ft}/30", help="Free throws field goals %")
    
    with col9 : 
        metricast, team_ast, team_rank_ast = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='AST',rank_column='rank_AST')
        st.metric(label = metricast, value = team_ast,delta=f"Rank {team_rank_ast}/30", help="Number of assists per match")
    
    with col10 : 
        metrictrb, team_trb, team_rank_trb = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='TRB',rank_column='rank_TRB')
        st.metric(label = metrictrb, value = team_trb,delta=f"Rank {team_rank_trb}/30", help="Number of rebounds per match")
    
    with col11 : 
        metricpace, team_pace, team_rank_pace = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='Pace',rank_column='rank_Pace')
        st.metric(label = metricpace, value = team_pace, delta=f"Rank {team_rank_pace}/30", help="Estimate of possessions per match")
    
    with col12 : 
        metricORtg, team_ORtg, team_rank_ORtg = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='ORtg',rank_column='rank_ORtg')
        st.metric(label = metricORtg, value = team_ORtg, delta=f"Rank {team_rank_ORtg}/30", help="Offensive rating: Estimate of points scored per 100 possessions")
    
    with col13 : 
        metricDRtg, team_DRtg, team_rank_DRtg = scorecards (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season,metric_column='DRtg',rank_column='rank_DRtg')
        st.metric(label = metricDRtg, value = team_DRtg, delta=f"Rank {team_rank_DRtg}/30", help="Defensive rating: Estimate of points allowed per 100 possessions")

with st.expander('Click for more stats'):
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col2 : 
            donutWL_fig = donutWL (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season)
            st.plotly_chart(donutWL_fig, theme='streamlit')

        with col1 : 
            shoot_fig = shootbyteam (df_cleaned_all_stats_light_final_22_23_24,option,st.session_state.selected_season)
            st.plotly_chart(shoot_fig, theme='streamlit')


    st.header('Major 5')

    with st.container():
        # major_5_fig = major5byteam (df_players_all_stats,option,st.session_state.selected_season)
        # st.plotly_chart(major_5_fig, theme='streamlit')
        #major5_PG=major5byteam(df_players_all_stats,option,st.session_state.selected_season,pos='PG')
        #st.write(major5_PG)
        #PG', 'SG', 'SF', 'PF', 'C'
        col1, col2, col3, col4, col5 = st.columns([1, 1,1, 1,1])
        with col1 : 
            maj5_PG=major5byteam2(df_players_all_stats,option,st.session_state.selected_season, position='PG')
            st.write(maj5_PG)
            # var_get_player_image_url = get_player_image_url(maj5_PG)
            # var_get_player_url = get_player_url(maj5_PG)
            # selected_player = maj5_PG
            # if selected_player:
            #     img_url = get_player_image_url(selected_player)
            # if img_url:
            #     st.image(img_url, width= 100, use_container_width=False)
            st.write('Point Guard')
        with col2 : 
            maj5_SG=major5byteam2(df_players_all_stats,option,st.session_state.selected_season, position='SG')
            st.write(maj5_SG)
            # var_get_player_image_url = get_player_image_url(maj5_SG)
            # var_get_player_url = get_player_url(maj5_SG)
            # selected_player = maj5_SG
            # if selected_player:
            #     img_url = get_player_image_url(selected_player)
            # if img_url:
            #     st.image(img_url, width= 100, use_container_width=False)
            st.write('Shooting Guard')
        with col3 : 
            maj5_PF=major5byteam2(df_players_all_stats,option,st.session_state.selected_season, position='PF')
            st.write(maj5_PF)
            # var_get_player_image_url = get_player_image_url(maj5_PF)
            # var_get_player_url = get_player_url(maj5_PF)
            # selected_player = maj5_PF
            # if selected_player:
            #     img_url = get_player_image_url(selected_player)
            # if img_url:
            #     st.image(img_url, width= 100, use_container_width=False)
            st.write('Power Forward')
        with col4 : 
            maj5_SF=major5byteam2(df_players_all_stats,option,st.session_state.selected_season, position='SF')
            st.write(maj5_SF)
            # var_get_player_image_url = get_player_image_url(maj5_SF)
            # var_get_player_url = get_player_url(maj5_SF)
            # selected_player = maj5_SF
            # if selected_player:
            #     img_url = get_player_image_url(selected_player)
            # if img_url:
            #     st.image(img_url, width= 100, use_container_width=False)
            st.write('Small Forward')
        with col5 : 
            maj5_C=major5byteam2(df_players_all_stats,option,st.session_state.selected_season, position='C')
            st.write(maj5_C)
            # var_get_player_image_url = get_player_image_url(maj5_C)
            # var_get_player_url = get_player_url(maj5_C)
            # selected_player = maj5_C
            # if selected_player:
            #     img_url = get_player_image_url(selected_player)
            # if img_url:
            #   st.image(img_url, width= 100, use_container_width=False)
            st.write('Center')


# ----------- Logo & stats
# 3. Win Loss chart
# with st.container():
#     col1, col2 = st.columns([1, 3])

#     with col1:
#         #st.write(scorecard_fig3P)
#         st.metric(metric3p, team_3p, f'Rank: {team_rank_3p}/30')
#         st.write(scorecard_figFT)
#         st.write(scorecard_figAST)
#         st.write(scorecard_figTRB)

#     with col2:
#         # st.title("Team Name")
#         # st.write("premier graph ici")
#         st.image("https://cdn.nba.com/logos/nba/1610612759/primary/L/logo.svg")
#         st.write(scorecard_fig2P)
#         st.write(scorecard_figPace)
#         st.write(scorecard_figORtg)
#         st.write(scorecard_figDRtg)
#         st.plotly_chart(shootbyteam_fig)
#         st.write(major5byteam_fig)

