import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import pandas_gbq

# Functions
#@st.cache_data(ttl=600)

def run_query(_client,_query):
    query_job = _client.query(_query)
    rows_raw = query_job.result()
# Convert to list of dicts. Required for st.cache_data to hash the return value.
    return pd.DataFrame([dict(row) for row in rows_raw])

### DF TEAMS
def import_teams_all_stats_light_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.all_stats_22_23_24_light;
    """
    return run_query(_client,sql)
def import_teams_global_ranking_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.global_ranking_WL_ratio_22_23_24;
    """
    return run_query(_client,sql)
def import_teams_victory_defeat_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.schedule_box_22_23_24;
    """
    return run_query(_client,sql)
def import_teams_shooting_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.type_shooting_per_team_22_23_24;
    """
    return run_query(_client,sql)

### DF PLAYERS
def import_players_advanced_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.players_advanced_22_23_24;
    """
    return run_query(_client,sql)
def import_players_regular_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.Players.total_players_regular_season_22_23_24;
    """
    return run_query(_client,sql)
def import_players_shooting_from_sql(_client):
    sql = """
    SELECT * FROM nba-baby-442813.final_datasets.shooting_players_22_23_24;
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


# Main
def main():
    # Title
    st.title("NBA BABYYYY")
    
    # Create API client.
    project_id = 'nba-baby-442813'
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)

    # Import datasets
    df_players1 = import_players_advanced_from_sql(client)
    df_players2 = import_players_regular_from_sql(client)
    df_players3 = import_players_shooting_from_sql(client)
    df_players4 = import_players_advanced_mean_from_sql(client)
    df_players5 = import_players_regular_mean_from_sql(client)

    df_teams1 = import_teams_all_stats_light_from_sql(client)
    df_teams2 = import_teams_global_ranking_from_sql(client)
    df_teams3 = import_teams_victory_defeat_from_sql(client)
    df_teams4 = import_teams_shooting_from_sql(client)

    # Display datasets
    st.write(df_teams4)





    # Front


if __name__ == "__main__":
    main()
