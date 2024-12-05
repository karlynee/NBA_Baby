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
import base64
import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode 
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

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


# Import datasets ------------------------------------------------------------
### DF TEAMS
def import_teams_all_stats_light_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.all_stats_22_23_24_light_final;
    """
    return run_query(_client,sql)

def import_teams_victory_defeat_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.schedule_box_clean_22_23_24;
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
    SELECT * FROM nba-baby-442813.final_datasets.player_mean_22_23_24;
    """
    return run_query(_client,sql)

# Imported datasets
    df_players_all_stats = import_players_all_stats_from_sql(client)
    df_player_mean_22_23_24 = import_players_advanced_mean_from_sql(client)

    df_cleaned_all_stats_light_final_22_23_24 = import_teams_all_stats_light_from_sql(client)
    df_cleaned_schedule_box_22_23_24 = import_teams_victory_defeat_from_sql(client)

# ------------------------ Import Graphs et Visualisations
# ----------------------------------- Teams ---------------------------------

### TEAMS - SCORE CARDS
def scorecards (df,team_name,season,metric_column,rank_column):
    # Filtrer sur l'équipe et la saison
    team_data = df[
    (df['Team'] == team_name) & (df['Season'] == season)
    ].iloc[0]
    # Récupérer le 3P% et son rank
    if "_" in metric_column:
        team_3p = team_data[metric_column]*100
    elif "ORtg" in metric_column:
        team_3p = team_data[metric_column]
    elif "DRtg" in metric_column:
        team_3p = team_data[metric_column]
    elif "Pace" in metric_column:
        team_3p = team_data[metric_column]
    else:
        team_3p = team_data[metric_column]/team_data['G']
    team_rank_3p = team_data[rank_column]
    # SCORECARD STREAMLIT
    #return st.metric(metric_column, team_3p, f'Rank: {int(team_rank_3p)}/30')
    return metric_column, round(team_3p,1), team_rank_3p
  # Créer un graphique vide
#   fig_team_3p = go.Figure()
#   suffix = ''
#   if "_" in metric_column: suffix = '%'

#   fig_team_3p.add_trace(go.Indicator(
#       mode="number",
#       value=team_3p,# Valeur du KPI
#       title={'text': f"{metric_column}",'font': {'size': 20}},  # Nom du KPI
#       number={'suffix': f"{suffix}", 'font': {'size': 40}},  # Taille de la valeur du KPI
#   ))

#   # Ajouter le rank
#   fig_team_3p.add_annotation(
#       x=0.5,
#       y=0.3,
#       text=f"Rank: {team_rank_3p}",
#       showarrow=False,
#       font=dict(size=15,color="red"),
#       align="center",
#       xanchor="center",
#       yanchor="top",
#       )

#   # Mise en page scorecard
#   fig_team_3p.update_layout(
#       height=220,
#       width=200,
#       showlegend=False,
#       margin=dict(t=50, b=50, l=20, r=20),
#       shapes=[
#           {
#               'type': 'rect',
#               'x0': 0,
#               'y0': 0,
#               'x1': 1,
#               'y1': 1,
#               'line': {
#                   'color': 'black',
#                   'width': 2
#               },
#               'fillcolor': 'rgba(255, 255, 255, 0)',
#           }
#       ]
#   )
#   return fig_team_3p

### TEAMS - Donut Chart Win Loss Global
def donutWL (df,team_name,season):
  # Filtrer sur l'équipe et la saison
  team_data = df[
  (df['Team'] == team_name) & (df['Season'] == season)].iloc[0]

  # Récupérer les chiffres de victoires et de défaites
  wins = team_data['W']
  losses = team_data['L']

  # Créer une nouvelle DF
  data = {'result': ['Wins', 'Losses'],'count': [wins, losses]}

  df_temp_WL = pd.DataFrame(data)

  # Donut Chart
  fig_team_WL = px.pie(df_temp_WL,
              names='result',
              values='count',
              color='count',
              color_discrete_sequence=['#1F4186','#C22737'],
              hole=0.4)

  fig_team_WL.update_layout(
      title = 'Win & Loss distribution per season',
      showlegend=True,
      height=400,
      width=500,
  )

  return fig_team_WL


### TEAMS - Shoot by team
def shootbyteam (df,team_name,season):
  # Filtrer sur l'équipe et la saison
  team_data = df[
  (df['Team'] == team_name) & (df['Season'] == season)].iloc[0]

  # Récupérer les types de shoot et leur nombre
  three_pts = team_data['_3PA']
  two_pts = team_data['_2PA']
  fts = team_data['FTA']


  # Créer une nouvelle DF
  data = {'type_shooting': ['3 points', '2 points','Free throws'],'count': [three_pts, two_pts,fts]}

  df_temp2 = pd.DataFrame(data)

  # Donut Chart
  fig_team_type_shoot = px.pie(df_temp2,
              title = 'Total shooting repartition',
              names='type_shooting',
              values='count',
              color_discrete_sequence=['#C22737','#222028','#1F4186'],
              hole=0.4)

  fig_team_type_shoot.update_layout(
      showlegend=True,
      height=400,
      width=500,
  )

  return fig_team_type_shoot


# ### TEAMS - Major 5 by team
# def major5byteam (df,team_name,season):
#     # Filtrer les données correspondant à l'équipe et à la saison choisies
#     player_data = df[(df['Team'] == team_name) & (df['Season'] == season)]
#     # Créer liste avec toutes les positions
#     positions = ['PG', 'SG', 'SF', 'PF', 'C']

#     # Créer liste vide pour y mettre le meilleur joueur par position
#     top_players = []  
#     for pos in positions:
#         pos_data = player_data[player_data['Pos'] == pos]
#         if not pos_data.empty:
#             top_player = pos_data.sort_values(by='GS', ascending=False).iloc[0]
#             top_players.append({'Game starters': top_player['Player'], 'Position': pos})
#         else:
#             top_players.append({'Game starters': 'N/A', 'Position': pos})

#     # Créer nouvelle DF avec les top players
#     top_players_df = pd.DataFrame(top_players)

#     # Tableau avec plotly
#     fig_startingfive = go.Figure(data=[go.Table(
#         header=dict(values=['Game starters', 'Position'],
#                     fill_color='lightskyblue',
#                     align='left'),
#         cells=dict(values=[top_players_df['Game starters'], top_players_df['Position']],
#                 fill_color='lightcyan',
#                 align='left'))
#     ])

#     fig_startingfive.update_layout(
#         width=500,
#         height=400
#     )

#     return fig_startingfive

def major5byteam2(df, team_name, season, position):
    # Filtrer les données correspondant à l'équipe, la saison et la position choisies
    player_data = df[(df['Team'] == team_name) & (df['Season'] == season) & (df['Pos'] == position)]
    
    if not player_data.empty:
        # Trier par 'GS' (Games Started) et sélectionner le meilleur joueur
        top_player = player_data.sort_values(by='GS', ascending=False).iloc[0]
        return top_player['Player']  # Return only the player's name
    else:
        return 'N/A'  # Return 'N/A' if no player is found for that position

### TEAMS - WIN LOSS GRAPH 
import streamlit as st
import pandas as pd


def win_loss(_df, _team_name, _season):
    # Filtrer les données sur l'équipe et la saison
    team_data = _df[(_df['Home_Team'] == _team_name) & (_df['Season'] == _season)]

    # S'assurer que la colonne 'Month' est sous forme de chaîne de caractères
    if isinstance(team_data['Month'].iloc[0], pd.Period):
        team_data['Month'] = team_data['Month'].astype(str)

    # Grouper les données par mois et résultats (Win/Loss)
    monthly_data = team_data.groupby(['Month', 'Home_WL']).size().reset_index(name='Count')

    # Extraire les mois uniques et garantir un ordre cohérent
    months = sorted(monthly_data['Month'].unique())

    # Séparer les données pour les victoires et les défaites
    wins = monthly_data[monthly_data['Home_WL'] == 1]
    losses = monthly_data[monthly_data['Home_WL'] == 0]

    # Remplir les valeurs manquantes pour les mois où il n'y a pas de données
    wins = wins.set_index('Month').reindex(months, fill_value=0).reset_index()
    losses = losses.set_index('Month').reindex(months, fill_value=0).reset_index()

    # Créer les barres pour les victoires et les défaites
    trace_wins = go.Bar(
        x=wins['Month'],
        y=wins['Count'],
        name='Wins',
        marker_color='#1F4186'
    )

    trace_losses = go.Bar(
        x=losses['Month'],
        y=losses['Count'],
        name='Losses',
        marker_color='#C22737'
    )

    # Créer la figure
    fig = go.Figure(data=[trace_wins, trace_losses])

    # Configurer la disposition
    fig.update_layout(
        title=f"Home Wins/Losses by Month in {_season}",
        xaxis_title="Month",
        yaxis_title="Count",
        barmode='group',
        legend_title="Result"
    )

    # Afficher la figure
    return fig

### TEAMS - NOUVEAU GRAPH A DEFINIR

### TEAMS - Scorecard Rank by Conference
def scorecard_rank(_df,_team_name,_season):
    # Filtrer la ligne correspondant à l'équipe choisie et la saison
    team_data = _df[(_df['Team'] == _team_name) & (_df['Season'] == _season)]

    if not team_data.empty:
    # If the data is not empty, retrieve the rank
        team_rank = team_data['rank_win_ratio'].iloc[0]
    else:
    # Handle case when no data is returned, assign a default value (e.g., NaN or a custom message)
        team_rank = None

    # SCORECARD STREAMLIT
    #return st.metric(label = 'Rank by Conference', value = f'{team_rank}/15', delta=None)
    return team_rank

def scorecard_conference(_df,_team_name,_season):
    # Filtrer la ligne correspondant à l'équipe choisie et la saison
    team_data = _df[(_df['Team'] == _team_name) & (_df['Season'] == _season)]

    if not team_data.empty:
    # If the data is not empty, retrieve the rank
        team_conference = team_data['Conference'].iloc[0]
    else:
    # Handle case when no data is returned, assign a default value (e.g., NaN or a custom message)
        team_conference = None

    # SCORECARD STREAMLIT
    #return st.metric(label = 'Rank by Conference', value = f'{team_conference}/15', delta=None)
    return team_conference

#   # Créer un graphique pour le Rank de l'équipe sélectionnée
#   fig_team_rank = go.Figure()

#   # Ajouter un trace pour l'indicateur Rank de cette équipe
#   fig_team_rank.add_trace(go.Indicator(
#     mode='number',
#     value=team_rank,
#     title={'text': f"Rank by Conference",'font':{'size':20}},
#     number={'suffix':'','font':{'size':40}},
#   ))
#   # Mise en page de la scorecard
#   fig_team_rank.update_layout(
#     height=210,  # Hauteur de la figure
#     width=260,
#     showlegend=False,  # Désactiver la légende
#     margin=dict(t=20, b=70, l=20, r=20),  # Ajuster les marges pour laisser de la place au rang
#     shapes=[  # Ajouter un rectangle autour de la scorecard
#         {
#             'type': 'rect',
#             'x0': 0,  # Position gauche
#             'y0': 0,  # Position bas
#             'x1': 1,  # Position droite
#             'y1': 1,  # Position haut
#             'line': {
#                 'color': 'black',  # Couleur de l'encadré
#                 'width': 2  # Épaisseur de la ligne
#             },
#             'fillcolor': 'rgba(255, 255, 255, 0)',  # Couleur de fond transparent
#         }
#     ]
#  )

#   # Afficher le graphique
#   return fig_team_rank

# ----------------------------------- Players ---------------------------------
### PLAYERS - PLAYER ID CARDS
def sc_pres2(_df, player_name, season, metric_column):
    # Filtrer la ligne correspondant à l'équipe choisie et la saison
    player_data = _df[(_df['Player'] == player_name) & (_df['Season'] == season)]
    # Récupérer le metric
    if "_" in metric_column:
        player_metric = player_data.iloc[0][metric_column]
    elif "Team" in metric_column:
        player_metric = player_data.iloc[0][metric_column]
    elif "Age" in metric_column:
        player_metric = player_data.iloc[0][metric_column]
    elif "Pos" in metric_column:
        player_metric = player_data.iloc[0][metric_column]
    elif "PER" in metric_column:
        player_metric = player_data.iloc[0][metric_column]
    else:
        player_metric = player_data.iloc[0][metric_column]
    # SCORECARD STREAMLIT
    #return st.metric(metric_column, player_metric, f'Rank: {int(team_rank_3p)}/30')
    return metric_column, str(player_metric)

# def sc_pres(df_players_all_stats, player_name, season, metric_column):
#     # Filtrer sur le joueur et la saison
#     player_data = df_players_all_stats[
#         (df_players_all_stats['Player'] == player_name) & (df_players_all_stats['Season'] == season)
#     ]

#     # Vérification qu'on a trouvé des données
#     if player_data.empty:
#         st.error(f"Pas de données trouvées pour le joueur '{player_name}' lors de la saison '{season}'")
#         return None

#     player_data = player_data.iloc[0]  # Extraire la première ligne

#     # Récupérer la métrique
#     if metric_column in player_data:
#         card = player_data[metric_column]
#     else:
#         st.error(f"La colonne '{metric_column}' n'existe pas dans les données du joueur.")
#         return None

#     # Vérifier si la métrique est numérique ou textuelle
#     if isinstance(card, (int, float, np.int64)):
#         suffix = '%' if "_" in metric_column else ''

#         # Créer un graphique pour une valeur numérique
#         fig_pres = go.Figure()
#         fig_pres.add_trace(go.Indicator(
#             mode="number",
#             value=card,
#             title={'text': f"{metric_column}", 'font': {'size': 20}},
#             number={'suffix': suffix, 'font': {'size': 40}},
#         ))

#     elif isinstance(card, str):
#         # Créer un graphique pour une valeur textuelle
#         fig_pres = go.Figure()
#         fig_pres.add_trace(go.Indicator(
#             mode="number+delta",
#             value=0,
#             title={'text': f"{metric_column}", 'font': {'size': 20}},
#             number={'prefix': f"{card}", 'font': {'size': 40}},
#         ))
#     else:
#         st.error(f"Type de donnée inattendu pour '{metric_column}': {type(card)}")
#         return None

#     # Mise en page scorecard
#     fig_pres.update_layout(
#         height=220,
#         width=800,
#         showlegend=False,
#         margin=dict(t=50, b=50, l=20, r=20),
#         shapes=[
#             {
#                 'type': 'rect',
#                 'x0': 0,
#                 'y0': 0,
#                 'x1': 1,
#                 'y1': 1,
#                 'line': {
#                     'color': 'black',
#                     'width': 2
#                 },
#                 'fillcolor': 'rgba(255, 255, 255, 0)',
#             }
#         ]
#     )

#     return fig_pres

### PLAYERS - JAUGES
#Code généré par Catalina
def jauge_players(player_name, season, df_players_all_stats):
    # Agréger les données par joueur et saison
    df_aggregated = df_players_all_stats.groupby(['Player', 'Season']).agg({
        'FT_': 'mean',   # Moyenne pour les pourcentages
        '_2P_': 'mean',  # Moyenne pour les pourcentages
        '_3P_': 'mean',  # Moyenne pour les pourcentages
        'TS_': 'mean',   # Moyenne pour les pourcentages
        'MP': 'sum',     # Somme pour les minutes jouées
        'PTS': 'sum'     # Somme pour les points marqués
    }).reset_index()

    # Filtrer les données pour le joueur et la saison sélectionnés
    players_graph_stats = df_aggregated[
        (df_aggregated['Player'] == player_name) &
        (df_aggregated['Season'] == season)
    ]

    # Vérifier si les données existent pour le joueur et la saison
    if players_graph_stats.empty:
        raise ValueError(f"Aucune donnée trouvée pour le joueur '{player_name}' durant la saison '{season}'.")

    # Extraire les valeurs nécessaires pour les jauges
    gauges_data = {
        "FT%": players_graph_stats['FT_'].iloc[0],
        "2P%": players_graph_stats['_2P_'].iloc[0],
        "3P%": players_graph_stats['_3P_'].iloc[0],
        "TS%": players_graph_stats['TS_'].iloc[0]
    }

    # Initialiser le graphique de jauges
    gauges = go.Figure()

    # Ajouter une jauge pour chaque statistique
    for i, (stat, value) in enumerate(gauges_data.items()):
        is_percentage = stat in ["FT%", "2P%", "3P%", "TS%"]
        gauges.add_trace(go.Indicator(
            mode="gauge+number",
            value=value * 100 if is_percentage else value,  # Convertir en pourcentage si nécessaire
            title={'text': stat},
            gauge={
                'axis': {'range': [0, 100] if is_percentage else [0, max(50, value + 10)]},
                'bar': {'color': "rgb(31,65,134,255)"},
                'steps': [{'range': [0, 100 if is_percentage else max(50, value + 10)], 'color': "lightgray"}],
            },
            domain={'x': [i % 2 * 0.45, i % 2 * 0.45 + 0.4],
                    'y': [1 - (i // 2) * 0.5 - 0.5, 1 - (i // 2) * 0.5]}
        ))

    # Mettre en page
    gauges.update_layout(
        title=f"Jauges des performances de {player_name} (Saison {season})",
        grid=dict(rows=3, columns=2),
        height=650
    )
    return gauges

    
### PLAYERS - DISTANCE TERRAIN
#Code généré par Catalina
def terrain(_df_players_all_stats,_player_filter, _season_filter):
  # Restructuration du DataFrame avec pd.melt
  df_FGA_dist = pd.melt(
      _df_players_all_stats,
      id_vars=["Player", "Season"],  # Colonnes à garder
      value_vars=[
          '_0_3___of_FGA_by_Distance',
          '_3_10___of_FGA_by_Distance',
          '_10_16___of_FGA_by_Distance',
          '_16_3P___of_FGA_by_Distance',
          '_3P___of_FGA_by_Distance'
      ],  # Colonnes à convertir
      var_name="distance",  # Nouveau nom pour les colonnes d'origine
      value_name="FGA_percent"  # Nouveau nom pour les valeurs
  )

  # Renommer les distances pour les rendre plus lisibles
  distance_mapping = {
      '_0_3___of_FGA_by_Distance': "0-3",
      '_3_10___of_FGA_by_Distance': "3-10",
      '_10_16___of_FGA_by_Distance': "10-16",
      '_16_3P___of_FGA_by_Distance': "16-3P",
      '_3P___of_FGA_by_Distance': "3P"
  }

  df_FGA_dist['distance'] = df_FGA_dist['distance'].replace(distance_mapping)

  # Affichage du DataFrame transformé
  df_FGA_dist = df_FGA_dist.groupby(['Player', 'Season', 'distance'])['FGA_percent'].mean().reset_index()
  df_FGA_dist


  # Charger l'image et la convertir en base64
  image_path = "images/terrain_final.jpg"  # Chemin de ton image uploadée
  with open(image_path, "rb") as image_file:
      base64_image = base64.b64encode(image_file.read()).decode("utf-8")

  # Filtres
  player_filter = _player_filter  # Nom du joueur à afficher
  season_filter = _season_filter  # Saison à afficher

  # Filtrer le DataFrame pour un joueur et une saison donnés
  df_filtered = df_FGA_dist[
      (df_FGA_dist["Player"] == player_filter) &
      (df_FGA_dist["Season"] == season_filter)
  ]

  # Données fictives pour les zones du terrain
  zones = df_filtered["distance"]
  pourcentages = df_filtered["FGA_percent"]  # Pourcentages (%FGA)


  # Définir les couleurs des zones
  colors = {
      "0-3": "rgba(31,65,134,0.4)",  # bleu
      "3-10": "rgba(31,65,134,0.4)",
      "10-16": "rgba(31,65,134,0.4)",
      "16-3P": "rgba(31,65,134,0.4)",
      "3P": "rgba(34,32,40,0.4)", # foncé
  }
  # Largeurs proportionnelles des barres
  zone_widths = {
      "0-3": 0.5,
      "3-10": 1,
      "10-16": 1.5,
      "16-3P": 0.5,
      "3P": 1.5,
  }
  # Padding entre les barres
  padding = 0.05
  # Calcul des positions dynamiques pour l'axe Y
  base_y = 0
  zone_positions = {}
  for zone in zones:
      zone_positions[zone] = base_y + zone_widths[zone] / 2  # Position centrale de la barre
      base_y += zone_widths[zone] + padding  # Ajout de la largeur et du padding
  # Création de la figure
  fig = go.Figure()
  # Ajout des barres avec largeur et position personnalisées
  for zone, pourcentage in zip(zones, pourcentages):
      fig.add_trace(
          go.Bar(
              x=[pourcentage],  # Valeur sur l'axe X (%FGA)
              y=[zone_positions[zone]],  # Position centrale sur l'axe Y
              orientation='h',  # Barres horizontales
              marker=dict(color=colors.get(zone, "rgba(200, 200, 200, 1.0)")),  # Couleur
              name=zone,
              width=zone_widths[zone],  # Largeur proportionnelle
              hovertemplate=f"{zone}: {pourcentage*100:.1f}%"  # Info au survol
          )
      )
  # Ajout de l'image en arrière-plan
  fig.add_layout_image(
      dict(
          source=f"data:image/png;base64,{base64_image}",  # Image en base64
          xref="paper",
          yref="paper",
          x=0,
          y=1,
          sizex=1,
          sizey=1,
          xanchor="left",
          yanchor="top",
          sizing="stretch",
          opacity=0.7,  # Transparence ajustée
          layer="below",
      )
  )
  # Personnalisation du layout
  fig.update_layout(
      title=f"Distribution des tirs par zone de {_player_filter} en {_season_filter}",
      xaxis=dict(title="%FGA", range=[0, 1]),  # Axe X
      yaxis=dict(
          title="",  # Supprime les titres de l'axe Y
          showgrid=False,
          tickvals=[zone_positions[zone] for zone in zones],  # Positions des ticks
          ticktext=zones,  # Labels correspondants
      ),
      template="plotly_white",
      bargap=0,  # Pas d'espace interne entre les barres
      height=600,  # Hauteur ajustée
      width=600,   # Largeur ajustée
  )

  # Affichage
  return fig

  #st.plotly_chart(terrain(df_players_all_stats,_player_filter, _season_filter)) #Streamlit

#### PLAYERS - SCORE CARDS
#Catalina
def players_scorecards(df, df2,_player_filter, _season_filter,metric_column):
    # Filtrer sur l'équipe et la saison
    player_data = df[
    (df['Player'] == _player_filter) & (df['Season'] == _season_filter)].iloc[0]
    player_mean_data = df2[(df2['season'] == _season_filter)].iloc[0]
    # Récupérer le 3P% et son rank
    if "_" in metric_column:
        player_metric = player_data[metric_column]
    elif "PTS" in metric_column:
        player_metric = player_data[metric_column]/player_data['G']
    elif "TRB" in metric_column:
        player_metric = player_data[metric_column]/player_data['G']
    elif "AST" in metric_column:
        player_metric = player_data[metric_column]/player_data['G']
    elif "STL" in metric_column:
        player_metric = player_data[metric_column]/player_data['G']
    elif "BLK" in metric_column:
        player_metric = player_data[metric_column]/player_data['G']
    elif "MP" in metric_column:
        player_metric = player_data[metric_column]/player_data['G']
    else:
        player_metric = player_data[metric_column]/player_data['G']
    if "_" in metric_column:
        mean_metric = player_mean_data[metric_column]
    elif "PTS" in metric_column:
        mean_metric = player_mean_data[metric_column]
    elif "TRB" in metric_column:
        mean_metric = player_mean_data[metric_column]
    elif "AST" in metric_column:
        mean_metric = player_mean_data[metric_column]
    elif "STL" in metric_column:
        mean_metric = player_mean_data[metric_column]
    elif "BLK" in metric_column:
        mean_metric = player_mean_data[metric_column]
    elif "MP" in metric_column:
        mean_metric = player_mean_data[metric_column]
    else:
        mean_metric = player_mean_data[metric_column]

    # SCORECARD STREAMLIT
    #return st.metric(metric_column, team_3p, f'Rank: {int(team_rank_3p)}/30')
    return metric_column, round(player_metric,1), mean_metric


# def players_scorecards(df_players_all_stats, mean_players_advanced_22_23_24, _player_filter, _season_filter):

#     # Filtrer les données pour le joueur et la saison dans les stats individuelles
#     player_stats = df_players_all_stats.query("Player == @_player_filter and Season == @_season_filter")
#     if player_stats.empty:
#         raise ValueError(f"Aucune donnée trouvée pour le joueur '{_player_filter}' et la saison '{_season_filter}'.")

#     # Filtrer les moyennes uniquement par saison
#     mean_stats = mean_players_advanced_22_23_24.query("season == @_season_filter")
#     if mean_stats.empty:
#         raise ValueError(f"Aucune donnée trouvée pour la saison '{_season_filter}'.")

#     # Statistiques à afficher
#     stats = ['PTS', 'TRB', 'AST', 'STL', 'BLK', 'MP']

#     sc_players = go.Figure()

#     # Ajouter les *scorecards* pour chaque statistique
#     for i, stat in enumerate(stats):
#         value = player_stats[stat].iloc[0]
#         mean_value = mean_stats[stat].mean()  # Moyenne sur toute la saison

#         # Configurer le suffixe et le mode d'affichage
#         suffix = '' if stat in ['PTS', 'MP', 'TRB', 'AST'] else '%'
#         # Modified: Define valueformat as a string
#         valueformat = f",.2f{suffix}"  # Example: ',.2f%' for percentage with 2 decimal places

#         # Ajouter une *scorecard*
#         sc_players.add_trace(go.Indicator(
#             mode="number",
#             value=value,
#             title={'text': f"<b>{stat}</b>", 'font': {'size': 18}},
#             # Modified: Use the string valueformat and set font size outside
#             number={'valueformat': valueformat, 'font': {'size': 30, 'color': 'rgba(31,65,134,255)'}},
#             domain={'row': i // 3, 'column': i % 3}
#         ))

#         # Ajouter l'annotation pour la moyenne
#         sc_players.add_annotation(
#             x=(i % 3) / 2.5 + 0.1,  # Ajuste pour positionner les annotations dans la grille
#             y=1 - (i // 3) / 1.5 - 0.3,
#             text=f"<span style='color: rgba(31,65,134,255);'>Moyenne : {mean_value:.2f}{suffix}</span>",
#             showarrow=False,
#             font=dict(size=12, color='rgba(31,65,134,255)'),
#             xanchor="center",
#             yanchor="top",
#         )


#     # Configuration générale
#     sc_players.update_layout(
#         grid=dict(rows=2, columns=3, pattern="independent"),
#         height=600,
#         width=900,
#         paper_bgcolor="white",
#         title={
#             'text': f"<b>Scorecards : {_player_filter} - Saison {_season_filter}</b>",
#             'x': 0.5,
#             'font': {'size': 22}
#         },
#         margin=dict(t=50, b=50, l=20, r=20)
#     )

#     # Mise en page de la figure
#     sc_players.update_layout(
#         template="plotly_dark",
#         grid={'rows': 2, 'columns': 3, 'pattern': "independent"},
#         height=600,
#         title=f"<b>Scorecards : {_player_filter} - Saison {_season_filter}</b>",
#         title_font_size=22,
#         title_x=0.5,
#         margin=dict(t=50, b=50, l=20, r=20),
#     )
#     return  sc_players


#### GLOBAL - RANK TOP 3 PLAYERS
#Code généré par Jeremy
def Rank_top_player(_df,_season):

    # Filtrer le DataFrame selon l'année sélectionnée
    df_player_top_y = _df[_df['Season'] == _season]

    # Fonction pour récupérer les 3 meilleures équipes pour une colonne donnée
    def top_3(_df, column):
        return _df.nlargest(3, column)[["Player", column]].reset_index(drop=True)

    # Récupérer les top 3 pour chaque colonne ("PTS", "TRB", "AST")
    top_PTS = top_3(df_player_top_y, "PTS")
    top_TRB = top_3(df_player_top_y, "TRB")
    top_AST = top_3(df_player_top_y, "AST")

    # Fusionner les résultats dans un seul DataFrame
    summary_table = pd.concat(
        [
            top_PTS.rename(columns={"PTS": "Score"}).assign(Criterion="Top 1"),
            top_TRB.rename(columns={"TRB": "Score"}).assign(Criterion="Top 2"),
            top_AST.rename(columns={"AST": "Score"}).assign(Criterion="Top 3")
        ]
    ).reset_index(drop=True)

    # Ajouter une colonne de "Rank" pour les positions (1er, 2ème, 3ème)
    summary_table['Rank'] = summary_table.index % 3 + 1

    # Créer une pivot table
    pivot_table = pd.pivot_table(
        summary_table,
        values="Player",  # Les équipes sont affichées dans les cellules
        index="Criterion",  # Les critères ("PTS", "TRB", "AST")
        columns="Rank",  # Les colonnes correspondent aux rangs (Top 1, Top 2, Top 3)
        aggfunc=lambda x: " / ".join(x),  # Si plusieurs équipes ont la même position, les concaténer
        fill_value="N/A"  # Valeur par défaut si un critère manque
    )

    # Renommer les colonnes pour plus de clarté
    pivot_table.columns = ["PTS", "TRB", "AST"]


    return pivot_table

### GLOBAL - RANK TOP 3 TEAMS
def Rank_top_teams(_df,_season):

  # Filtrer le DataFrame selon l'année sélectionnée
  df_rk_team = _df[_df['Season'] == _season]

  # Fonction pour récupérer les 3 meilleures équipes pour une colonne donnée
  def top_3(df, column):
      return df.nlargest(3, column)[["Team", column]].reset_index(drop=True)

  # Récupérer les top 3 pour chaque colonne ("ORtg", "TRB", "AST")
  rank_ORtg = top_3(df_rk_team, "ORtg")
  rank_TRB = top_3(df_rk_team, "TRB")
  rank_AST = top_3(df_rk_team, "AST")

  # Fusionner les résultats dans un seul DataFrame
  summary_table = pd.concat(
      [
          rank_ORtg.rename(columns={"ORtg": "Score"}).assign(Criterion="Top 1"),
          rank_TRB.rename(columns={"TRB": "Score"}).assign(Criterion="Top 2"),
          rank_AST.rename(columns={"AST": "Score"}).assign(Criterion="Top 3")
      ]
  ).reset_index(drop=True)

  # Ajouter une colonne de "Rank" pour les positions (1er, 2ème, 3ème)
  summary_table['Rank'] = summary_table.index % 3 + 1

  # Créer une pivot table
  pivot_table = pd.pivot_table(
      summary_table,
      values="Team",  # Les équipes sont affichées dans les cellules
      index="Criterion",  # Les critères ("A", "D", "M")
      columns="Rank",  # Les colonnes correspondent aux rangs (Top 1, Top 2, Top 3)
      aggfunc=lambda x: " / ".join(x),  # Si plusieurs équipes ont la même position, les concaténer
      fill_value="N/A"  # Valeur par défaut si un critère manque
  )

  # Renommer les colonnes pour plus de clarté
  pivot_table.columns = ["ORtg", "TRB", "AST"]

  return pivot_table


### GLOBAL - RANK CONFERENCE
def Rank_conference_W_E(_df,_season):

    # Filtrage des données selon la saison sélectionnée
    df_rk_top = _df[_df["Season"] == _season]  # rank_win_ratio, Team, Conference, W, L, Win_Ratio

    # Filtrage des données pour les conférences ouest et est
    df_RK_filtered_West = df_rk_top[df_rk_top["Conference"] == "West"].round(2).sort_values(by="rank_win_ratio", ascending=True)
    df_RK_filtered_East = df_rk_top[df_rk_top["Conference"] == "East"].round(2).sort_values(by="rank_win_ratio", ascending=True)

    # Sélection des colonnes que vous souhaitez afficher
    columns_to_display = ["rank_win_ratio", "Team", "Conference", "W", "L", "Win_Ratio"]  # Exemple des colonnes souhaitées
    df_RK_filtered_West = df_RK_filtered_West[columns_to_display]
    df_RK_filtered_East = df_RK_filtered_East[columns_to_display]

    # Rename the column "rank_win_ratio" to "Rank" after selecting the columns
    df_RK_filtered_West = df_RK_filtered_West.rename(columns={"rank_win_ratio": "Rank"})
    df_RK_filtered_East = df_RK_filtered_East.rename(columns={"rank_win_ratio": "Rank"})

    # Vérifier si les données ne sont pas vides
    if df_RK_filtered_West.empty or df_RK_filtered_East.empty:
        print(f"Aucune donnée trouvée pour la saison {_season}. Vérifiez les filtres.")
    else:
        # Création de sous-graphiques
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("West Conference", "East Conference"),
            specs=[[{"type": "table"}, {"type": "table"}]]
        )

        # Ajout du tableau pour la Conférence West
        fig.add_trace(
            go.Table(
                columnwidth=[4, 4, 4, 3, 3],  # Largeur des colonnes
                header=dict(
                    values=df_RK_filtered_West.columns,
                    align="center",
                    fill_color='lightblue',
                    font=dict(size=12)
                ),
                cells=dict(
                    values=[df_RK_filtered_West[col] for col in df_RK_filtered_West.columns],
                    align="center",
                    height=30
                )
            ),
            row=1, col=1
        )

        # Ajout du tableau pour la Conférence East
        fig.add_trace(
            go.Table(
                columnwidth=[4, 4, 4, 3, 3],
                header=dict(
                    values=df_RK_filtered_East.columns,
                    align="center",
                    fill_color='lightblue',
                    font=dict(size=12)
                ),
                cells=dict(
                    values=[df_RK_filtered_East[col] for col in df_RK_filtered_East.columns],
                    align="center",
                    height=30
                )
            ),
            row=1, col=2
        )

        # Mise en page
        fig.update_layout(
            height=600,
            width=1400,
        )

    return fig

# GLOBAL - SCORECARD YESTERDAY'S MATCH
# ----------------------- Ne pas utiliser
# def draw_scorecard(team1_name, team1_score, team2_name, team2_score):
#     fig, ax = plt.subplots()
#     ax.scatter(6, 3)
#     ax.set_xlim(0, 1)
#     ax.set_ylim(0, 1)
#     ax.axis("off")

#     # Ajouter un rectangle autour
#     ax.add_patch(Rectangle((0.05, 0.2), 0.9, 0.6, fill=None, edgecolor="black", lw=2))

#     # Ajouter les noms des équipes
#     ax.text(0.3, 0.7, team1_name, ha="center", va="center", fontsize=16, fontweight="bold", color="blue")
#     ax.text(0.7, 0.7, team2_name, ha="center", va="center", fontsize=16, fontweight="bold", color="red")

#     # Ajouter les scores
#     ax.text(0.3, 0.4, str(team1_score), ha="center", va="center", fontsize=20, color="black")
#     ax.text(0.7, 0.4, str(team2_score), ha="center", va="center", fontsize=20, color="black")

#     # Ajouter "vs" au centre
#     ax.text(0.5, 0.55, "vs", ha="center", va="center", fontsize=16, color="black", fontstyle="italic")
#     return fig

def yesterday_results(yesterday):
    # Étape 1 : Déterminer la date de la veille
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Construire l'URL de la page de boxscores
    base_url = "https://www.basketball-reference.com/boxscores/"
    url = f"{base_url}?month={yesterday.split('-')[1]}&day={yesterday.split('-')[2]}&year={yesterday.split('-')[0]}"

    # Étape 2 : Récupérer le contenu de la page
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    results = []  # List to store all the game results

    if response.status_code != 200:
        print(f"Erreur lors de l'accès à la page : {response.status_code}")
        return results  # Return the empty list if there's an error

    else:
    # Étape 3 : Analyser le HTML avec BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        games = soup.find_all('div', class_='game_summary')
        
    if not games:
        print("No matches found for this date.")
        return results
    else:
        for game in games:
            # Récupérer les équipes
            team_rows = game.find_all('tr')
            if len(team_rows) >= 2:
                # Ligne de la première équipe
                team1_name = team_rows[0].find('a').text
                team1_score = int(team_rows[0].find_all('td')[1].text)
                # Ligne de la deuxième équipe
                team2_name = team_rows[1].find('a').text
                team2_score = int(team_rows[1].find_all('td')[1].text)
                # Fonction pour dessiner une "scorecard"
                # draw_scorecard(team1_name, team1_score, team2_name, team2_score)
                results.append((team1_name, team1_score, team2_name, team2_score))


    return results

# def create_scorecard_match_yesterday():
# # Étape 1 : Déterminer la date de la veille
#     yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    
#     # Construire l'URL de la page de boxscores
#     base_url = "https://www.basketball-reference.com/boxscores/"
#     url = f"{base_url}?month={yesterday.split('-')[1]}&day={yesterday.split('-')[2]}&year={yesterday.split('-')[0]}"

#     # Étape 2 : Récupérer le contenu de la page
#     headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#     }
#     response = requests.get(url, headers=headers)
    
#     if response.status_code != 200:
#         print(f"Erreur lors de l'accès à la page : {response.status_code}")
#     else:
#     # Étape 3 : Analyser le HTML avec BeautifulSoup
#         soup = BeautifulSoup(response.text, 'html.parser')
#         games = soup.find_all('div', class_='game_summary')
        
#     if not games:
#         print("Aucun match trouvé pour cette date.")
#     else:
#         for game in games:
#             # Récupérer les équipes
#             team_rows = game.find_all('tr')
#             if len(team_rows) >= 2:
#                 # Ligne de la première équipe
#                 team1_name = team_rows[0].find('a').text
#                 team1_score = int(team_rows[0].find_all('td')[1].text)
#                 # Ligne de la deuxième équipe
#                 team2_name = team_rows[1].find('a').text
#                 team2_score = int(team_rows[1].find_all('td')[1].text)
#                 # Fonction pour dessiner une "scorecard"
#                 # draw_scorecard(team1_name, team1_score, team2_name, team2_score)



# -------------------------------------------- Scraping ----------------------------------------
# Logo Team
# Code generated by Karlyne & Thomas
def get_team_logos (_team_name):
  # Step 1: Get the HTML content of the webpage
  url = "https://www.nba.com/teams"
  response = requests.get(url)
  if response.status_code != 200:
    print(f"Erreur lors de l'accès à {player_url} : {response.status_code}")
    return None

  soup = BeautifulSoup(response.content, 'html.parser')

  # Step 2: Find the first image in the webpage
  img_tag = soup.find('img', {'title': f'{_team_name} Logo'})  # You can use find_all if you want multiple images

  # Step 3: Extract the image URL
  if img_tag:
    img_url = img_tag['src']
    return img_url
  else:
    print(f"Logo de {_team_name} introuvable sur la page.")
    return None


# Photo Player
# Code generated by Thomas

def get_player_url(player_name):
    # Séparer le prénom et le nom
    name_parts = player_name.lower().split()

    # Le nom de famille est la dernière partie
    last_name = unidecode(name_parts[-1])

    # Le prénom est la première partie
    first_name = unidecode(name_parts[0])

    # Créer le format d'URL en utilisant la première lettre du nom de famille
    last_initial = last_name[0]
    last_name_part = last_name[:5]  # Première partie du nom de famille
    url = f"https://www.basketball-reference.com/players/{last_initial}/{last_name_part}{first_name[:2]}01.html"

    return url

# Fonction pour récupérer l'URL de la photo d'un joueur
def get_player_image_url(player_name):
    # Récupérer l'URL de la page du joueur
    player_url = get_player_url(player_name)
    print (player_name)
    # Étape 1 : Récupérer la page joueur
    response = requests.get(player_url)
    print(response)
    if response.status_code != 200:
        print(f"Erreur lors de l'accès à {player_url} : {response.status_code}")
        return None

    # Étape 2 : Analyser le HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    # Étape 3 : Trouver l'image du joueur (en vérifiant l'attribut alt pour le nom du joueur)
    #img_tag = soup.find('img', {'alt': re.compile(rf"Photo of {re.escape(player_name)}", re.IGNORECASE)})
    img_tag = soup.find('img', {'itemscope': 'image'})

    print(img_tag)

    if img_tag:
        img_url = img_tag['src']

        # Vérifier si l'URL est absolue ou relative
        if not img_url.startswith("http"):
            img_url = f"https://www.basketball-reference.com{img_url}"
            print(img_url)
        return img_url
    else:
        print(f"{player_name} photo is unavailable.")
        return None



# ----------------------------- total players --------------------------------------------
def call_players() : 
   return ['Kevin Knox', 'Goran Dragić', 'Eugene Omoruyi', 'Duncan Robinson', 'Matt Ryan', 'Danny Green', 'Matthew Dellavedova', 'Meyers Leonard', 'Jason Preston', 'Jordan Hall', 'Ryan Arcidiacono', 'Mac McClung', 'Sam Merrill', 'Micah Potter', 'Gabe York', 'Tyrese Martin', 'Louis King', 'Buddy Boeheim', 'Justin Champagnie', 'Facundo Campazzo', 'Lester Quiñones', 'Kendall Brown', 'Joe Wieskamp', 'Mfiondu Kabengele','Marko Simonovic', 'Malcolm Hill', 'David Roddy', 'Tre Mann', 'Malachi Flynn', 'Doug McDermott', 'Evan Fournier', 'Shake Milton', 'Patty Mills', 'Collin Gillespie', 'Jaylen Nowell', 'Terquavion Smith', "Jahmi'us Ramsey", 'Dylan Windler', 'Jalen Pickett', 'Gabe Vincent', 'Daishen Nix', 'Chris Livingston',  'Admiral Schofield', 'Isaiah Mobley', 'Jamaree Bouyea', 'Taze Moore', 'Seth Lundy', 'TyTy Washington Jr.', 'Timmy Allen', 'Jordan Miller', 'Jordan Ford', 'Keyontae Johnson', 'R.J. Hampton', 'Mason Jones', 'Izaiah Brockington', 'Adam Flagler', 'Saddiq Bey', 'Malik Beasley', 'Reggie Jackson', 'Luke Kennard', 'Payton Pritchard', 'Garrison Mathews', 'Rodney McGruder', 'Saben Lee', 'Jamal Cain', 'Theo Pinson', 'Skylar Mays', 'Frank Kaminsky', 'Terry Taylor', 'Dru Smith', 'Vit Krejci', 'Cody Martin', 'Keon Ellis', 'Ryan Rollins', 'PJ Dozier', 'Tony Bradley', 'Michael Carter-Williams', 'RaiQuan Gray', 'Leandro Bolmaro', 'Bojan Bogdanović', 'Alec Burks', 'Gordon Hayward', 'Jordan Nwora', 'Danilo Gallinari', 'Troy Brown Jr.', 'Svi Mykhailiuk', 'Aleksej Pokusevski', 'Tosan Evbuomwan', 'Luka Garza', 'Kira Lewis Jr.', 'Jules Bernard', 'Jeenathan Williams', 'Brandon Williams', 'Jeff Dowtin', 'James Bouknight', 'Armoni Brooks', 'Cole Swider', 'T.J. Warren', 'Dexter Dennis', 'Braxton Key', 'JD Davison', "D'Moi Hodge", 'DaQuan Jeffries', 'Dereon Seabron', 'Jacob Toppin', 'Maxwell Lewis', 'James Johnson', 'Jack White', 'Andrew Funk',  'Bones Hyland', 'Terrence Ross', 'Dario Šarić', 'Boban Marjanović', 'Bryn Forbes', 'Nikola Jović', 'Kemba Walker', 'Luka Šamanić', 'Trent Forrest', 'Garrett Temple', 'Lindell Wigginton',  'Jarrett Culver', 'Shaquille Harrison', 'Omer Yurtseven',  'Joshua Primo', 'Udonis Haslem', 'Jarrell Brantley', 'Gradey Dick', 'Marcus Morris', 'Ben Sheppard', 'Keita Bates-Diop', 'Derrick Rose', 'Thaddeus Young', "Devonte' Graham",  'Kenneth Lofton Jr.', 'Gui Santos', 'Onuralp Bitim', 'AJ Griffin',  'DeJon Jarreau', 'Emoni Bates', 'Joe Harris', 'Nate Hinton', 'Jermaine Samuels', 'Kobi Simmons', 'Wenyen Gabriel', 'Kendrick Nunn', 'Will Barton', 'George Hill', 'Juan Toscano-Anderson', 'Bruno Fernando', 'Furkan Korkmaz', 'Johnny Juzang', 'Thanasis Antetokounmpo', 'Jaden Springer', 'Immanuel Quickley', 'Tyler Herro', 'Cameron Payne',  'Dalano Banton', 'Vasilije Micić', 'Davion Mitchell',
    'Quentin Grimes', 'Dāvis Bertāns', 'Seth Curry', 'Rayan Rupert',
    'A.J. Lawson', 'Markieff Morris', 'Cory Joseph', 'Sidy Cissoko',
    'Zavier Simpson', 'Xavier Moon', 'Matthew Hurt', 'Jerome Robinson',
    'Robin Lopez', 'Mike Conley', 'Austin Rivers', 'Jordan McLaughlin',
    'Raul Neto', 'Jake LaRavia', 'Gary Payton II', 'Cody Zeller',
    'Davon Reed', 'Jonathan Isaac', 'Jay Huff', 'Xavier Cooks',
    'Justin Jackson', 'Jaden Hardy', 'LaMelo Ball', 'Nicolas Batum',
    'Caleb Houstan', 'A.J. Green', 'Jalen Wilson',
    'Javon Freeman-Liberty', 'Ish Smith', 'Olivier-Maxence Prosper',
    'Jeremiah Robinson-Earl', 'Kessler Edwards', 'Mãozinha Pereira',
    'Mouhamed Gueye', 'Malik Williams', 'Greg Brown III',
    'Jalen McDaniels', 'Josh Green', 'Kevin Love', 'Khris Middleton',
    'Mike Muscala', 'Landry Shamet', 'Mo Bamba', 'Ty Jerome',
    'Sandro Mamukelashvili', 'Darius Bazley', 'Dewayne Dedmon',
    'Blake Wesley', 'Amir Coffey', 'Julian Champagnie', 'Kevon Harris',
    'Dalen Terry', 'Kennedy Chandler', 'Khem Birch', 'Olivier Sarr',
    'Trevelin Queen', 'Justin Minaya', 'Anfernee Simons',
    'Simone Fontecchio', 'Dante Exum', 'Joe Ingles', 'Marcus Smart',
    'Lamar Stevens', 'Ja Morant', 'Jarred Vanderbilt', 'Ousmane Dieng',
    'Isaiah Livers', 'Reggie Bullock', 'Kobe Bufkin', 'Colby Jones',
    'Josh Minott', 'Otto Porter Jr.', 'Tyus Jones', 'Coby White',
    'Collin Sexton', 'Cameron Johnson', 'Bryce McGowens',
    'Ziaire Williams', 'Stanley Johnson', 'Ricky Rubio',
    'Nathan Knight', 'Jae Crowder', 'Juancho Hernangómez',
    'Tim Hardaway Jr.', 'Jordan Clarkson', 'Andrew Nembhard',
    'Chris Paul', 'Aaron Holiday', 'Kyle Lowry', 'Brice Sensabaugh',
    'Andre Jackson Jr.', 'Kobe Brown', 'Brandon Clarke', 'Taj Gibson',
    'Malaki Branham', 'Damion Lee', 'Cam Thomas', 'Thomas Bryant',
    'James Wiseman', 'Nickeil Alexander-Walker', 'Moses Moody',
    "Jae'Sean Tate", 'MarJon Beauchamp', 'Cade Cunningham',
    'Isaiah Roby', 'Frank Ntilikina', 'Max Christie', 'KZ Okpala',
    'Darius Garland', 'Keyonte George', 'Miles McBride',
    'Jordan Hawkins', 'Chimezie Metu', 'Julian Strawther',
    'Sasha Vezenkov', 'Lindy Waters III', 'Stanley Umude',
    'Yuta Watanabe', 'Chuma Okeke', 'Julian Phillips',
    'Tristan Vukcevic', 'Marques Bolden', 'Spencer Dinwiddie',
    "D'Angelo Russell", 'Tyrese Maxey', 'Eric Gordon', 'Isaiah Joe',
    'Cam Reddish', 'Johnny Davis', 'Moussa Diabaté', 'Dennis Schröder',
    'T.J. McConnell', 'Bruce Brown', 'Malcolm Brogdon', 'Zach LaVine',
    'Jared Butler', 'Chris Duarte', 'Delon Wright', 'Oshae Brissett',
    'Monte Morris', 'Javonte Green', 'Orlando Robinson', 'Trae Young',
    'Tre Jones', 'Corey Kispert', 'Josh Hart', 'Josh Richardson',
    'Justin Holiday', 'Blake Griffin', 'Mamadi Diakite', 'John Butler',
    'Nerlens Noel', 'Terry Rozier', 'RJ Barrett', 'Kenrich Williams',
    'Xavier Tillman Sr.', 'Ashton Hagans', 'Kevin Durant',
    'Harrison Barnes', 'Russell Westbrook', 'Goga Bitadze',
    'Pascal Siakam', 'Gary Trent Jr.', 'Dillon Brooks',
    'Scotty Pippen Jr.', 'Richaun Holmes', 'Nassir Little',
    'Keldon Johnson', 'Cedi Osman', 'Pat Connaughton', 'Dyson Daniels',
    'Justise Winslow', 'Peyton Watson', 'Alex Len', 'Buddy Hield',
    'KJ Martin', 'Anthony Gill', 'Wesley Matthews', 'Leaky Black',
    'Kyrie Irving', 'Max Strus', 'Rui Hachimura', 'Obi Toppin',
    'Trendon Watford', 'Terence Davis', 'Gary Harris', 'John Wall',
    'Théo Maledon', 'Jaylin Williams', 'Damian Jones', 'Julius Randle',
    'Kelly Olynyk', 'Marcus Sasser', 'Precious Achiuwa',
    'Naji Marshall', 'Dennis Smith Jr.', 'Bennedict Mathurin',
    'Moritz Wagner', 'Romeo Langford', 'Willy Hernangómez',
    'Jabari Walker', 'Jalen Brunson', 'Scoot Henderson', 'OG Anunoby',
    'Patrick Beverley', 'Jared Rhoden', 'Grayson Allen',
    'Georges Niang', 'Vlatko Čančar', 'Matisse Thybulle',
    'Gorgui Dieng', 'Marvin Bagley III', 'Tristan Thompson',
    'Dominick Barlow', 'Taurean Prince', 'Aaron Wiggins',
    'Ochai Agbaji', 'Josh Christopher', 'Terance Mann',
    "Royce O'Neale", 'Markelle Fultz', 'Craig Porter Jr.',
    'Patrick Baldwin Jr.', 'Mikal Bridges', 'Bobby Portis',
    'Zion Williamson', 'Dorian Finney-Smith', 'Hamidou Diallo',
    "De'Andre Hunter", "De'Anthony Melton", 'Jevon Carter',
    'Noah Clowney', 'Robert Covington', 'Franz Wagner', 'Jaden Ivey',
    'Devin Vassell', 'Lonnie Walker IV', 'Karl-Anthony Towns',
    'Jeff Green', 'Christian Braun', 'Jimmy Butler', 'Cam Whitmore',
    'Mason Plumlee', 'Charles Bassey', 'Damian Lillard', 'Jalen Green',
    'Devin Booker', 'Norman Powell', 'Bogdan Bogdanović', 'Rudy Gay',
    'Mouhamadou Gueye', 'Dejounte Murray', 'Brandon Ingram',
    'Austin Reaves', 'Jaxson Hayes', 'Talen Horton-Tucker',
    'Trey Lyles', 'Larry Nance Jr.', 'Tari Eason', 'Stephen Curry',
    'Paul George', 'Anthony Lamb', 'Jaime Jaquez Jr.', 'Killian Hayes',
    'Dwight Powell', 'JaVale McGee', 'Jontay Porter', 'Jordan Poole',
    'Sam Hauser', 'Dean Wade', 'Anthony Black', 'Torrey Craig',
    'Desmond Bane', 'Ish Wainright', "De'Aaron Fox", 'Luguentz Dort',
    'Jeremy Sochan', 'JaMychal Green', 'Zeke Nnaji', 'JT Thor',
    'DeAndre Jordan', 'Kevin Huerter', 'Ben Simmons', 'GG Jackson II',
    'Chris Boucher', 'Josh Okogie', 'Jrue Holiday',
    'Tyrese Haliburton', 'John Konchar', 'Montrezl Harrell', 'Bol Bol',
    'Jaylen Brown', 'Ayo Dosunmu', 'Jordan Goodwin', 'Lauri Markkanen',
    'Donovan Mitchell', 'Andre Drummond', 'Bradley Beal',
    'P.J. Washington', 'Grant Williams', 'Kawhi Leonard',
    'Andrew Wiggins', 'Jericho Sims', 'Trey Murphy III',
    'Wendell Carter Jr.', 'Kris Dunn', 'Klay Thompson', 'Kyle Kuzma',
    'Deni Avdija', 'Kevon Looney', 'Isaac Okoro', 'Jock Landale',
    'Maxi Kleber', 'Kai Jones', 'Haywood Highsmith',
    'Taylor Hendricks', 'Josh Giddey', 'James Harden', 'Cole Anthony',
    'Caleb Martin', 'Jonathan Kuminga', 'LeBron James',
    "Day'Ron Sharpe", 'Luka Dončić', 'Miles Bridges', 'Toumani Camara',
    'Patrick Williams', 'Christian Wood', 'Aaron Nesmith',
    'Isaiah Stewart', 'Jerami Grant', 'Caris LeVert',
    'Vince Williams Jr.', 'Jalen Williams', 'DeMar DeRozan',
    'Donte DiVincenzo', 'Cason Wallace', 'CJ McCollum',
    'Fred VanVleet', 'Duop Reath', 'Jalen Smith', 'Amen Thompson',
    'Domantas Sabonis', 'Paolo Banchero', 'Jamal Murray', 'Malik Monk',
    'Tobias Harris', 'Keegan Murray', 'Anthony Edwards',
    'Deandre Ayton', 'Kentavious Caldwell-Pope', 'Jaden McDaniels',
    'Jayson Tatum', 'Jusuf Nurkić', 'Aaron Gordon', 'Alex Caruso',
    'Steven Adams', 'Luke Kornet', 'Alperen Sengun', 'Nikola Jokić',
    'Kelly Oubre Jr.', 'Jalen Suggs', 'Jalen Johnson', 'Jalen Duren',
    'Kyle Anderson', 'Draymond Green', 'Santi Aldama',
    'Robert Williams', 'Bilal Coulibaly', 'Zach Collins',
    'Giannis Antetokounmpo', 'Paul Reed', 'Derrick Jones Jr.',
    'Daniel Theis', 'Jonas Valančiūnas', 'Naz Reid',
    'Michael Porter Jr.', 'Nikola Vučević', 'Christian Koloko',
    'Ausar Thompson', 'Onyeka Okongwu', 'Bam Adebayo',
    'Scottie Barnes', 'Al Horford', 'Jabari Smith Jr.', 'John Collins',
    'Isaiah Jackson', 'Drew Eubanks', 'Herbert Jones',
    'Isaiah Hartenstein', 'Shai Gilgeous-Alexander', 'Joel Embiid',
    'Evan Mobley', 'Derrick White', 'Dereck Lively II', 'Clint Capela',
    'Jarrett Allen', 'Rudy Gobert', 'Ivica Zubac',
    'Kristaps Porziņģis', 'Jaren Jackson Jr.', 'Anthony Davis',
    'Myles Turner', 'Nic Claxton', 'Walker Kessler', 'Brook Lopez',
    'Chet Holmgren', 'Victor Wembanyama', 'Moses Brown',
    'Brandon Boston Jr.', 'Michael Foster Jr.', 'Alondes Williams',
    'Trey Jemison', 'Filip Petrušev', 'Malcolm Cazalon',
    'Ron Harper Jr.', 'Javonte Smart', 'David Duke Jr.',
    'Vernon Carey Jr.', 'Duane Washington Jr.', 'Wendell Moore Jr.',
    'Danuel House Jr.', 'P.J. Tucker', 'Kevin Porter Jr.',
    'Jacob Gilyard', 'Trevor Keels', 'Jordan Schakel',
    'Sterling Brown', 'Deonte Burton', 'Harry Giles', 'D.J. Carton',
    'Pat Spencer', 'Kaiser Gates', 'Jarace Walker', 'Kris Murray',
    'Leonard Miller', 'Chima Moneke', 'Chris Silva', 'Adama Sanogo',
    'Colin Castleton', 'Quenton Jackson', 'Markquis Nowell',
    'Jalen Crutcher', 'Dmytro Skapintsev', 'Chance Comanche',
    'Oscar Tshiebwe', 'Neemias Queta', 'Bismack Biyombo',
    'Udoka Azubuike', 'Nathan Mensah', 'Mark Williams', 'Ibou Badji',
    'Jakob Poeltl', 'Mitchell Robinson', 'Daniel Gafford',
    'Jay Scrubb', 'Ricky Council IV', 'McKinley Wright IV',
    'Pete Nance', 'Usman Garuba', 'Noah Vonleh', 'Hunter Tyson',
    'Charlie Brown Jr.', 'Carlik Jones', 'Tyler Dorsey',
    'Donovan Williams', 'Devon Dotson', 'Isaiah Thomas',
    'Edmond Sumner', 'Shaedon Sharpe', 'Keon Johnson',
    'Brandon Miller', 'Nick Richards', 'Trayce Jackson-Davis',
    'Xavier Sneed', 'Jordan Walsh', 'Henri Drell', 'Dariq Whitehead',
    'Andre Iguodala', 'Jose Alvarado', 'Nick Smith Jr.', 'Isaiah Todd',
    'Victor Oladipo', 'Drew Peterson', 'Darius Days', 'Jett Howard',
    'E.J. Liddell', 'Trevor Hudgins', 'Brandin Podziemski',
    'Alize Johnson', 'Frank Jackson', 'Amari Bailey', 'Alex Fudge',
    'Isaiah Wong', 'Jalen Slawson', 'Jalen Hood-Schifino',
    'D.J. Wilson', 'Serge Ibaka']


#--------------------------------------------------------------------PRED------------------------------------------------------#
# UTILS
def save_model_with_pickle(model, filename):
    """
    Save the trained model to a .pkl file using the pickle library.

    Args:
        model: The trained machine learning model to be saved.
        filename (str): The path and name of the file to save the model (e.g., 'model.pkl').

    Returns:
        None
    """
    try:
        with open(filename, 'wb') as file:
            pickle.dump(model, file)
        print(f"Model successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving model: {e}")

def load_model_with_pickle(filename):
    """
    Load a model from a .pkl file using the pickle library.

    Args:
        filename (str): The path and name of the .pkl file containing the saved model.

    Returns:
        model: The loaded machine learning model.
    """
    try:
        with open(filename, 'rb') as file:
            model = pickle.load(file)
        #print(f"Model successfully loaded from {filename}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

#nba_data_schedules_23_24_25
# SCRAP SCHEDULE
def scrape_schedule_season_data(year):
    # Construire l'URL pour la saison donnée
    base_url = f"https://www.basketball-reference.com/leagues/NBA_{year}_games.html"
    print(base_url)
    response = requests.get(base_url)
    print(response)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    # Trouver les liens pour les mois (October à April)
    links = soup.find_all('a', text=['October', 'November', 'December', 'January', 'February', 'March', 'April'])
    print(links)
    # Récupérer les tableaux pour chaque mois
    all_data = []
    for link in links:
        print(link['href'])
        month_url = "https://www.basketball-reference.com" + link['href']
        monthly_tables = pd.read_html(month_url)
        table = monthly_tables[0]  # Supposons que le premier tableau contient les données
        table['Year'] = year  # Ajouter une colonne pour l'année
        all_data.append(table)
    print(f'all data >> {all_data}')
    # Combiner les données mensuelles pour la saison
    season_data = pd.concat(all_data, axis=0)
    return season_data

def combine_scraped_schedule_2_years(year1=2024,year2=2025):
  print('>>')
  nba_data_2024 = scrape_schedule_season_data(year1)
  print('>>>')
  print(nba_data_2024.head(1))
  nba_data_2025 = scrape_schedule_season_data(year2)
  print(nba_data_2025.head(1))
  nba_data_schedules_23_24_25 = pd.concat([nba_data_2024, nba_data_2025], axis=0)
  nba_data_schedules_23_24_25 = nba_data_schedules_23_24_25.rename(columns={"Visitor/Neutral": "Team1",
                                                                          "PTS": "Team1Score",
                                                                          "Home/Neutral": "Team2",
                                                                          "PTS.1": "Team2Score",
                                                                          })
  return nba_data_schedules_23_24_25

# SCRAPE MATCHS PER TEAMS
def scrape_matches_per_teams():
      # URL de la page des stats "Per Game"
  url = "https://www.basketball-reference.com/leagues/NBA_2025.html"

  # Headers pour éviter d'être bloqué par le site
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

  # Envoyer une requête GET pour récupérer le contenu de la page
  response = requests.get(url, headers=headers)

  if response.status_code != 200:
      print(f"Erreur lors de l'accès à la page : {response.status_code}")
  else:
      # Parser le contenu HTML
      soup = BeautifulSoup(response.text, "html.parser")

      # Trouver le tableau "Per Game"
      table = soup.find("table", {"id": "per_game-team"})

      if table:
          # Extraire les en-têtes
          headers = [th.text for th in table.find("thead").find_all("th")]
          headers = headers[1:]  # Ignorer la première colonne vide

          # Extraire les lignes du tableau
          rows = []
          for row in table.find("tbody").find_all("tr"):
              # Vérifier si la ligne n'est pas un séparateur
              if row.find("th", {"scope": "row"}):
                  cells = [cell.text.strip() for cell in row.find_all("td")]
                  rows.append(cells)

          # Créer un DataFrame Pandas
          df_teams_pergame_24_25 = pd.DataFrame(rows, columns=headers)
  return df_teams_pergame_24_25

def merge_scraped_matches_per_teams_bq_pred_prep(df_teams_pergame_24_25, nba_data_schedules_23_24_25):
  # Enclose dataset and table names in backticks (`)
  sql = "SELECT * FROM `nba-baby-442813.Teams.per_game_23_24`;"

  df_teams_pergame_23_24 = pd.read_gbq(sql, project_id="nba-baby-442813", dialect="standard")
  df_teams_pergame_23_24 = df_teams_pergame_23_24.rename(columns={
    "FG_": "FG%",
    "_3P": "3P",
    "_3PA": "3PA",
    "_3P_": "3P%",
    "_2P": "2P",
    "_2PA": "2PA",
    "_2P_": "2P%",
    "FT_": "FT%",
  })
  df_teams_pergame_23_24_25 = pd.concat([df_teams_pergame_23_24, df_teams_pergame_24_25], ignore_index=True)
  df_teams_pergame_23_24_25 = df_teams_pergame_23_24_25.drop(["Rk"], axis=1)
  df_teams_pergame_23_24_25 = df_teams_pergame_23_24_25.drop(df_teams_pergame_23_24_25 [df_teams_pergame_23_24_25 ['Team'] == 'League Average'].index)
  conditions = [
    nba_data_schedules_23_24_25['Team1Score'] > nba_data_schedules_23_24_25['Team2Score'],
    nba_data_schedules_23_24_25['Team1Score'] < nba_data_schedules_23_24_25['Team2Score']
  ]
  choices=[1,0]
  nba_data_schedules_23_24_25['Team1Win'] = np.select(conditions, choices, 1)
  # Mergings the nba_data_schedules_23_24_25 and stats datasets, adding a prefix depending on which teams stats are being used
  df_prediction_base = nba_data_schedules_23_24_25.merge(df_teams_pergame_23_24_25.add_prefix('Team1'), how='left', left_on=['Team1'],
                    right_on=['Team1Team']).drop(['Team1Team'],
                                                  axis=1).merge(df_teams_pergame_23_24_25.add_prefix('Team2'),
                                                                              how='left', left_on=['Team2'],
                                                                              right_on=['Team2Team']).drop(['Team2Team'],axis=1)
  df_prediction_base = df_prediction_base.drop(["Unnamed: 6", "Unnamed: 7","Date","Attend.","LOG","Arena","Notes","Year","Start (ET)"], axis=1)
  return df_prediction_base

# PREDICTION
def label_encoder_teams_pred():
  teams = [
    'Los Angeles Lakers', 'Phoenix Suns', 'Houston Rockets',
    'Boston Celtics', 'Washington Wizards', 'Atlanta Hawks',
    'Detroit Pistons', 'Minnesota Timberwolves', 'Cleveland Cavaliers',
    'New Orleans Pelicans', 'Oklahoma City Thunder',
    'Sacramento Kings', 'Dallas Mavericks', 'Portland Trail Blazers',
    'Philadelphia 76ers', 'Denver Nuggets', 'New York Knicks',
    'Miami Heat', 'Toronto Raptors', 'Brooklyn Nets',
    'Los Angeles Clippers', 'Orlando Magic', 'Golden State Warriors',
    'Chicago Bulls', 'Memphis Grizzlies', 'Indiana Pacers',
    'Utah Jazz', 'San Antonio Spurs', 'Milwaukee Bucks',
    'Charlotte Hornets'
  ]
  # Encodage avec LabelEncoder
  le = LabelEncoder()
  le.fit(teams)
  # Dictionnaire des équipes avec leur encodage numérique
  dict_encoded_teams = {team: int(le.transform([team])[0]) for team in teams}
  # Affichage du dictionnaire
  return dict_encoded_teams

def train_and_export_model_as_pkl(df_prediction_base_path,dict_encoded_teams): 
  df_prediction_base = pd.read_csv(df_prediction_base_path)
  df_prediction_base['Team1'] = df_prediction_base['Team1'].replace(dict_encoded_teams)
  df_prediction_base['Team2'] = df_prediction_base['Team2'].replace(dict_encoded_teams)
  df_prediction_base = df_prediction_base.dropna().drop(columns=['Team2Score','Team1Score'], axis = 1)
  log_reg = LogisticRegression()
  X = df_prediction_base.drop(columns=['Team1Win'])
  y = df_prediction_base['Team1Win']
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
  #scaler = StandardScaler()
  #X_train = scaler.fit_transform(X_train)
  # apply same transformation on X_test
  #X_test = scaler.transform(X_test)
  # train model
  clf = LogisticRegression(solver='lbfgs', max_iter=1000)
  clf.fit(X_train, y_train)
  # store predictions
  y_pred = clf.predict(X_test)
  save_model_with_pickle(clf,'LR_model.pkl')  


def predict_team1_win(_team1_name, _team2_name, df_prediction_base_path, model, dict_encoded_teams):
    """
    Predict if Team1 will win against Team2 using a trained Logistic Regression model.
    
    Args:
        team1_name (str): Name of Team1
        team2_name (str): Name of Team2
        df (pd.DataFrame): DataFrame containing team statistics
        model: Trained logistic regression model
        scaler: Scaler used for preprocessing (if any, e.g., StandardScaler)
    
    Returns:
        float: Probability of Team1 winning
        int: Predicted label (0 or 1)
    """
    df_prediction_base = pd.read_csv(df_prediction_base_path)
    team1_name = dict_encoded_teams[_team1_name]
    team2_name = dict_encoded_teams[_team2_name]
    df_prediction_base['Team1'] = df_prediction_base['Team1'].replace(dict_encoded_teams)
    df_prediction_base['Team2'] = df_prediction_base['Team2'].replace(dict_encoded_teams)
    df_prediction_base = df_prediction_base.dropna().drop(columns=['Team2Score','Team1Score','Team1Win'], axis = 1)
    team1_stats = df_prediction_base[df_prediction_base['Team1'] == team1_name].iloc[0].filter(like='Team1')
    team2_stats = df_prediction_base[df_prediction_base['Team2'] == team2_name].iloc[0].filter(like='Team2')
    # Combine the features into a single row
    combined_features = pd.concat([team1_stats, team2_stats]).to_frame().T
    #print(combined_features)
    columns = list(combined_features.columns)
    columns.remove('Team2')  # Remove 'Team2' from its current position
    columns.insert(1, 'Team2')  # Insert 'Team2' at index 1
    # Reorder the DataFrame
    combined_features = combined_features[columns]
    display(combined_features)
    # Predict the probability and label
    probability = model.predict_proba(combined_features)[:, 1][0]  # Probability of Team1 winning
    prediction = model.predict(combined_features)[0]  # 0 or 1

    return probability, prediction