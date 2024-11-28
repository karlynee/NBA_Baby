import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import pandas_gbq

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)

# Exemple de requête
sql = """
 SELECT * FROM nba-baby-442813.Players.players_advanced_22_23;
"""
project_id = 'nba-baby-442813'
df = pandas_gbq.read_gbq(sql, project_id=project_id)


st.write(
    df
)

