# Page helpers.py: imports et fonctions

#### streamlit run nba_app.py

# Imports de librairies
import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import pandas_gbq
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Cache Data
#st.cache_data(ttl=600)

# Create API client
def get_bigquery_client():
    project_id = 'nba-baby-442813'
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    #client = bigquery.Client(credentials=credentials)
    return bigquery.Client(credentials=credentials)

# Execute a generic SQL query and return them in DataFrame
def run_query(_client,_query):
    query_job = _client.query(_query)
    rows_raw = query_job.result()
    return pd.DataFrame([dict(row) for row in rows_raw])

# Imported datasets
    #df_players1 = import_players_all_stats_from_sql(client)
    #df_players4 = import_players_advanced_mean_from_sql(client)
    #df_players5 = import_players_regular_mean_from_sql(client)

    df_teams1 = import_teams_all_stats_light_from_sql(client)
    df_teams2 = import_teams_victory_defeat_from_sql(client)


# Import datasets
### DF TEAMS
def import_teams_all_stats_light_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.all_stats_22_23_24_light_final;
    """
    return run_query(_client,sql)

def import_teams_victory_defeat_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.schedule_box_22_23_24;
    """
    return run_query(_client,sql)

### DF PLAYERS
def import_players_all_stats_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.players_all_stats;
    """
    return run_query(_client,sql)

def import_players_advanced_mean_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.mean_players_advenced_22_23_24;
    """
    return run_query(_client,sql)

def import_players_regular_mean_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.mean_players_regular_season_22_23_24;
    """
    return run_query(_client,sql)


# Import Graphs et Visualisations
### SCORE CARDS - TEAMS
def teams_score_card(df_teams1, kpi):
    #Filtre sur l'equipe et la saison
    team_name="Sacramento Kings"
    season = "22-23"
    # Filtrer la ligne correspondant à l'équipe choisie et la saison
    team_data = df_teams1[
        (df_teams1['Team'] == team_name) & (df_teams1['Season'] == season)
    ].iloc[0]
    # Récupérer le 3P% et son rang depuis les colonnes correspondantes
    team_3p = team_data['_3P_']
    team_rank_3p = team_data['rank_3P_']
    # Créer un graphique pour le 3P% de l'équipe sélectionnée
    fig_team_3p = go.Figure()
    # Ajouter un trace pour l'indicateur 3P% de cette équipe
    fig_team_3p.add_trace(go.Indicator(
    mode="number",
    value=team_3p*100,  # Valeur du 3P% pour l'équipe sélectionnée
    title={'text': f"3P%",'font': {'size': 20}},  # Titre avec le nom de l'équipe
    number={'suffix': '%', 'font': {'size': 40}},  # Le chiffre en grand avec un espace
    ))
    # Ajouter une annotation pour afficher le rang de l'équipe
    fig_team_3p.add_annotation(
    x=0.5,  # Position X (centrée)
    y=0.3,  # Position Y en dessous de l'indicateur
    text=f"Rank: {team_rank_3p}",
    showarrow=False,
    font=dict(size=15,color="red"),
    align="center",
    xanchor="center",
    yanchor="top",
    )
    # Mise en page de la scorecard
    fig_team_3p.update_layout(
    height=220,  # Hauteur de la figure
    width=200,
    showlegend=False,  # Désactiver la légende
    margin=dict(t=50, b=50, l=20, r=20),  # Ajuster les marges pour laisser de la place au rang
    shapes=[  # Ajouter un rectangle autour de la scorecard
            {
            'type': 'rect',
            'x0': 0,  # Position gauche
            'y0': 0,  # Position bas
            'x1': 1,  # Position droite
            'y1': 1,  # Position haut
            'line': {
                'color': 'black',  # Couleur de l'encadré
                'width': 2  # Épaisseur de la ligne
            },
            'fillcolor': 'rgba(255, 255, 255, 0)',  # Couleur de fond transparent
            }
            ]
        )
    
    return st.plotly_chart(fig_team_3p) 




