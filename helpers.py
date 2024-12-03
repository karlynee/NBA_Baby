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

  # Créer un graphique vide
  fig_team_3p = go.Figure()
  suffix = ''
  if "_" in metric_column: suffix = '%'

  fig_team_3p.add_trace(go.Indicator(
      mode="number",
      value=team_3p,# Valeur du KPI
      title={'text': f"{metric_column}",'font': {'size': 20}},  # Nom du KPI
      number={'suffix': f"{suffix}", 'font': {'size': 40}},  # Taille de la valeur du KPI
  ))

  # Ajouter le rank
  fig_team_3p.add_annotation(
      x=0.5,
      y=0.3,
      text=f"Rank: {team_rank_3p}",
      showarrow=False,
      font=dict(size=15,color="red"),
      align="center",
      xanchor="center",
      yanchor="top",
      )

  # Mise en page scorecard
  fig_team_3p.update_layout(
      height=220,
      width=200,
      showlegend=False,
      margin=dict(t=50, b=50, l=20, r=20),
      shapes=[
          {
              'type': 'rect',
              'x0': 0,
              'y0': 0,
              'x1': 1,
              'y1': 1,
              'line': {
                  'color': 'black',
                  'width': 2
              },
              'fillcolor': 'rgba(255, 255, 255, 0)',
          }
      ]
  )
  return fig_team_3p

### TEAMS - Donut Chart Win Loss Global
def donutWL (df,team_name,season):
  # Filtrer sur l'équipe et la saison
  team_data = df[
  (df['Team'] == team_name) & (df['Season'] == season)].iloc[0]

  # Récupérer les chiffres de victoires et de défaites
  wins = team_data['W']
  losses = team_data['L']

  # Créer une nouvelle DF
  data = {'result': ['W', 'L'],'count': [wins, losses]}

  df_temp_WL = pd.DataFrame(data)

  # Donut Chart
  fig_team_WL = px.pie(df_temp_WL,
              names='result',
              values='count',
              color_discrete_map={'W': 'blue', 'L': 'red'},
              hole=0.4)

  fig_team_WL.update_layout(
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
  data = {'type_shooting': ['_3PA', '_2GA','FTA'],'count': [three_pts, two_pts,fts]}

  df_temp2 = pd.DataFrame(data)

  # Donut Chart
  fig_team_type_shoot = px.pie(df_temp2,
              names='type_shooting',
              values='count',
              color_discrete_map={'_3PA': 'light blue', '_2PA': 'red','FTA':'blue'},
              hole=0.4)

  fig_team_type_shoot.update_layout(
      showlegend=True,
      height=400,
      width=500,
  )

  return fig_team_type_shoot


### TEAMS - Major 5 by team
# def major5byteam (df,team_name,season):
#   # Filtrer les données correspondant à l'équipe et à la saison choisies
#   player_data = df[
#       (df['Team'] == team_name)
#       (df['Season'] == season)
#   ]

#   # Créer liste avec toutes les positions
#   positions = ['PG', 'SG', 'SF', 'PF', 'C']

#   # Créer liste vide pour y mettre le meilleur joueur par position
#   top_players = []

#   for pos in positions:
#       pos_data = player_data[player_data['Pos'] == pos]
#       if not pos_data.empty:
#           top_player = pos_data.sort_values(by='GS', ascending=False).iloc[0]
#           top_players.append({'Game starters': top_player['Player'], 'Position': pos})
#       else:
#           top_players.append({'Game starters': 'N/A', 'Position': pos})

#   # Créer nouvelle DF avec les top players
#   top_players_df = pd.DataFrame(top_players)

#   # Tableau avec plotly
#   fig_startingfive = go.Figure(data=[go.Table(
#       header=dict(values=['Game starters', 'Position'],
#                   fill_color='lightskyblue',
#                   align='left'),
#       cells=dict(values=[top_players_df['Game starters'], top_players_df['Position']],
#                 fill_color='lightcyan',
#                 align='left'))
#   ])

#   fig_startingfive.update_layout(
#       width=500,
#       height=400
#   )

#   return fig_startingfive.show()

### TEAMS - WIN LOSS GRAPH 
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
        marker_color='green'
    )

    trace_losses = go.Bar(
        x=losses['Month'],
        y=losses['Count'],
        name='Losses',
        marker_color='red'
    )

    # Créer la figure
    fig = go.Figure(data=[trace_wins, trace_losses])

    # Configurer la disposition
    fig.update_layout(
        title=f"{_team_name}: Home Wins/Losses by Month in {_season}",
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

  # Créer un graphique pour le Rank de l'équipe sélectionnée
  fig_team_rank = go.Figure()

  # Ajouter un trace pour l'indicateur Rank de cette équipe
  fig_team_rank.add_trace(go.Indicator(
    mode='number',
    value=team_rank,
    title={'text': f"Rank by Conference",'font':{'size':20}},
    number={'suffix':'','font':{'size':40}},
  ))
  # Mise en page de la scorecard
  fig_team_rank.update_layout(
    height=210,  # Hauteur de la figure
    width=260,
    showlegend=False,  # Désactiver la légende
    margin=dict(t=20, b=70, l=20, r=20),  # Ajuster les marges pour laisser de la place au rang
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

  # Afficher le graphique
  return fig_team_rank

# ----------------------------------- Players ---------------------------------
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
                'bar': {'color': "blue"},
                'steps': [{'range': [0, 100 if is_percentage else max(50, value + 10)], 'color': "lightgray"}],
            },
            domain={'x': [i % 2 * 0.5, i % 2 * 0.5 + 0.5],
                    'y': [1 - (i // 2) * 0.5 - 0.5, 1 - (i // 2) * 0.5]}
        ))

    # Mettre en page
    gauges.update_layout(
        title=f"Jauges des performances de {player_name} (Saison {season})",
        grid=dict(rows=3, columns=2),
        height=950
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
  image_path = "images/terrain.jpg"  # Chemin de ton image uploadée
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

#### RANK TOP 3 PLAYERS
#Code généré par Jeremy
def Rank_top_player(df,season):

    # Ma datafram
    data = df
    df_top_players = pd.DataFrame(data)

    # Ajouter une variable pour sélectionner l'année
    #selected_year = "22-23" #valeur a changer selon l'année

    # Filtrer le DataFrame selon l'année sélectionnée
    df_player_top_y = df_top_players[df_top_players['Season'] == season]

    # Fonction pour récupérer les 3 meilleures équipes pour une colonne donnée
    def top_3(df, column):
        return df.nlargest(3, column)[["Player", column]].reset_index(drop=True)

    # Récupérer les top 3 pour chaque colonne ("A", "D", "M")
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
        index="Criterion",  # Les critères ("A", "D", "M")
        columns="Rank",  # Les colonnes correspondent aux rangs (Top 1, Top 2, Top 3)
        aggfunc=lambda x: " / ".join(x),  # Si plusieurs équipes ont la même position, les concaténer
        fill_value="N/A"  # Valeur par défaut si un critère manque
    )

    # Renommer les colonnes pour plus de clarté
    pivot_table.columns = ["PTS", "TRB", "AST"]


    return pivot_table

### RANK TOP 3 TEAMS
def Rank_top_teams(_df,_season):
  
  # Filtrer le DataFrame selon l'année sélectionnée
  df_rk_team = _df[_df['Season'] == _season]

  # Fonction pour récupérer les 3 meilleures équipes pour une colonne donnée
  def top_3(df, column):
      return df.nlargest(3, column)[["Team", column]].reset_index(drop=True)
  
  print(df_rk_team.columns)
  # Récupérer les top 3 pour chaque colonne ("A", "D", "M")
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

### RANK CONFERENCE
def Rank_conference_W_E(_df,season):

    df_rk_top = _df[_df["Season"] == season]  # rank_win_ratio, Team, Conference, W, L, Win_Ratio

    # Filtrage des données pour les conférences ouest et est
    df_RK_filtered_West = df_rk_top[df_rk_top["Conference"] == "West"].round(2)
    df_RK_filtered_East = df_rk_top[df_rk_top["Conference"] == "East"].round(2)

    # Sélection des colonnes que vous souhaitez afficher
    columns_to_display = ["rank_win_ratio", "Team", "Conference", "W", "L", "Win_Ratio"]  # Exemple des colonnes souhaitées
    df_RK_filtered_West = df_RK_filtered_West[columns_to_display]
    df_RK_filtered_East = df_RK_filtered_East[columns_to_display]

    # Rename the column "rank_win_ratio" to "Rank" after selecting the columns
    df_RK_filtered_West = df_RK_filtered_West.rename(columns={"rank_win_ratio": "Rank"})
    df_RK_filtered_East = df_RK_filtered_East.rename(columns={"rank_win_ratio": "Rank"})

    # Vérifier si les données ne sont pas vides
    if df_RK_filtered_West.empty or df_RK_filtered_East.empty:
        print(f"Aucune donnée trouvée pour la saison {season}. Vérifiez les filtres.")
    else:
        # Création de sous-graphiques
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Classement Conférence West", "Classement Conférence Est"),
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
            title_text=f"Classement par conférence ({season})",
            title_x=0.5,
            title_font=dict(size=20)
        )

    return fig

# --------------------------------- Scraping ----------------------------------------
# Fonction pour générer l'URL du joueur en fonction de son nom
# Code generated by Thomas
def get_player_url(player_name):
    # Séparer le prénom et le nom
    name_parts = player_name.lower().split()

    # Le nom de famille est la dernière partie
    last_name = name_parts[-1]

    # Le prénom est la première partie
    first_name = name_parts[0]

    # Créer le format d'URL en utilisant la première lettre du nom de famille
    last_initial = last_name[0]
    last_name_part = last_name[:5]  # Première partie du nom de famille
    url = f"https://www.basketball-reference.com/players/{last_initial}/{last_name_part}{first_name[:2]}01.html"

    return url

# Fonction pour récupérer l'URL de la photo d'un joueur
def get_player_image_url(player_name):
    # Récupérer l'URL de la page du joueur
    player_url = get_player_url(player_name)

    # Étape 1 : Récupérer la page joueur
    response = requests.get(player_url)
    if response.status_code != 200:
        print(f"Erreur lors de l'accès à {player_url} : {response.status_code}")
        return None

    # Étape 2 : Analyser le HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Étape 3 : Trouver l'image du joueur (en vérifiant l'attribut alt pour le nom du joueur)
    img_tag = soup.find('img', {'alt': re.compile(rf"Photo of {re.escape(player_name)}", re.IGNORECASE)})

    if img_tag:
        img_url = img_tag['src']

        # Vérifier si l'URL est absolue ou relative
        if not img_url.startswith("http"):
            img_url = f"https://www.basketball-reference.com{img_url}"

        return img_url
    else:
        print(f"Photo de {player_name} introuvable sur la page.")
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