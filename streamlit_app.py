import streamlit as st
st.write("Yooooo")
st.write("How are you")
#jhfei
import pandas as pd
#import table total_stats_23_24
sql = "SELECT * FROM nba-baby-442813.Teams.total_stats_23_24;"
df_stats2324 = pd.read_gbq(sql,project_id="nba-baby-442813",dialect="standard")
df_stats2324.head()
