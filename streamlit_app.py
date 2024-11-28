import streamlit as st
from google.oauth2 import service_account
from google.cloud import bigquery
from google.oauth2 import id_token
from google.auth.transport import requests
import pandas as pd
import pandas_gbq

@st.cache_data(ttl=600)
def run_query(_client,_query):
    query_job = _client.query(_query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.cache_data to hash the return value.
    rows = [dict(row) for row in rows_raw]
    return rows

def main():
    st.title("NBA BABYYYY")
    # Create API client.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials)
    sql = """
    SELECT * FROM nba-baby-442813.Players.players_advanced_22_23_24;
    """
    rows = run_query(client,sql)

    # Print results.
    st.write("Some wise words from Shakespeare:")
    st.write(rows)
    
if __name__ == "__main__":
    main()
